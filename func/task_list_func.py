import datetime

from config import *
from button import *
from func.function import *


@logger.catch
async def create_show_tasks_kb(chat, page=0, task_list='all'):
    tasks = await get_ten_tasks(chat, page, task_list)
    kb_task = InlineKeyboardMarkup(row_width=5)
    for n, task in enumerate(tasks):
        kb_task.insert(InlineKeyboardButton(text=f'{str(n + page * 10 + 1)}', callback_data=cb_task.new(task_id=task.id, page=page)))
    if len(tasks) < 10:
        for _ in range(10 - len(tasks)):
            kb_task.insert(InlineKeyboardButton(text='-', callback_data='not_button'))
    btn_new_task = InlineKeyboardButton(emojize(':memo:Новая задача'), callback_data=cb_new_task.new(chat_id=chat.chat_id))
    btn_excel_task = InlineKeyboardButton(text='Excel', callback_data=cb_excel_tasks.new(chat_id=chat.chat_id))
    text_button = ':backhand_index_pointing_right:Неделя' if task_list == 'week' else 'Неделя'
    btn_week_task = InlineKeyboardButton(text=emojize(text_button), callback_data=cb_week_tasks.new(chat_id=chat.chat_id))
    text_button = ':backhand_index_pointing_right:Месяц' if task_list == 'month' else 'Месяц'
    btn_month_task = InlineKeyboardButton(text=emojize(text_button), callback_data=cb_month_tasks.new(chat_id=chat.chat_id))
    text_button = ':backhand_index_pointing_right:Все' if task_list == 'all' else 'Все'
    btn_all_task = InlineKeyboardButton(text=emojize(text_button), callback_data=cb_all_tasks.new(chat_id=chat.chat_id))
    if page > 0:
        kb_task.row(InlineKeyboardButton(text='<<', callback_data=cb_page_list_task.new(chat_id=chat.chat_id, page=page - 1)))
    kb_task.insert(btn_new_task)
    if page < (await get_count_tasks(chat, task_list) - 1) // 10:
        kb_task.insert(InlineKeyboardButton(text='>>', callback_data=cb_page_list_task.new(chat_id=chat.chat_id, page=page + 1)))
    kb_task.row(btn_week_task, btn_month_task, btn_all_task, btn_excel_task)
    kb_task.row(btn_back_chat_task)
    return kb_task


@logger.catch
async def create_show_tasks_mes(chat, user_id, page=0, task_list='all'):
    tasks = await get_ten_tasks(chat, page, task_list)
    text = 'Все задачи'
    if task_list == 'week':
        text = 'Задачи текущей недели'
    if task_list == 'month':
        text = 'Задачи текущего месяца'
    mes = emojize(f'<u>{text} чата <b>{chat.title}</b> ({await get_count_tasks(chat, task_list)}):</u>')
    for n, task in enumerate(tasks):
        warning = ':warning:' if not task.description or not task.date_end or len(task.for_user) == 0 else ''
        complete = ':check_mark_button:' if task.completed else ':cross_mark:'
        my_task = ''
        if len(task.for_user) > 0:
            my_task = ':face_with_monocle:' if user_id == task.for_user[0].user_id else ''
        mes += emojize(f'\n{complete} <b>{str(n + page * 10 + 1)}.</b> <i>{task.date_end.strftime("%d.%m.%Y")}</i> {my_task} <b>{task.title}</b> {warning}')
    return mes


@logger.catch
async def create_show_chat_for_tasks_kb(user):
    kb_chat = InlineKeyboardMarkup(row_width=1)
    for part in user.participants:
        kb_chat.insert(InlineKeyboardButton(text=part.chat.title, callback_data=cb_chat_task.new(chat_id=part.chat.chat_id)))
    return kb_chat


@logger.catch
async def del_task_by_id(task_id):
    session.query(Task).filter(Task.id == task_id).delete()
    session.query(TaskForUser).filter(TaskForUser.task_id == task_id).delete()
    session.commit()


@logger.catch
async def get_this_week_month_tasks(chat_id, wm):
    start_date, stop_date = await start_stop_date(wm)
    tasks = session.query(Task).filter(
        Task.chat_id == chat_id, Task.date_end >= start_date, Task.date_end < stop_date).order_by(Task.date_end).all()
    return tasks, start_date, stop_date


@logger.catch
async def get_excel_task(chat_id, task_list='all'):
    if task_list == 'month':
        start_date, stop_date = await start_stop_date('month')
        task_pd = pd.read_sql(session.query(Task).filter(Task.chat_id == chat_id,
                                      Task.date_end >= start_date, Task.date_end <= stop_date).order_by(Task.date_end).statement, engine)
    elif task_list == 'week':
        start_date, stop_date = await start_stop_date('week')
        task_pd = pd.read_sql(session.query(Task).filter(Task.chat_id == chat_id,
                                           Task.date_end >= start_date, Task.date_end < stop_date).order_by(Task.date_end).statement, engine)
    else:
        task_pd = pd.read_sql(session.query(Task).filter(Task.chat_id == chat_id).order_by(Task.date_end).statement, engine)
    task_pd = task_pd.drop(task_pd.columns[[0, 1, 5, 8, 9, 12]], axis=1)
    task_pd = task_pd.rename(columns={'title': 'Задача', 'description': 'Описание', 'user_id_create': 'Автор задачи',
                                      'completed': 'Выполнено'})
    list_date_create, list_date_end, list_date_complete = [], [], []
    for i in range(len(task_pd['Автор задачи'])):
        if task_pd['Выполнено'][i]:
            task_pd['Выполнено'][i] = 'Выполнено'
        else:
            task_pd['Выполнено'][i] = 'Не выполнено'

        user = await get_user(int(task_pd['Автор задачи'][i]))
        task_pd['Автор задачи'][i] = user.name
        try:
            list_date_create.append(task_pd['date_create'][i].strftime("%d.%m.%Y %H:%M"))
        except (ValueError, AttributeError):
            list_date_create.append(None)
        try:
            list_date_end.append(task_pd['date_end'][i].strftime("%d.%m.%Y"))
        except (ValueError, AttributeError):
            list_date_end.append(None)
        try:
            list_date_complete.append(task_pd['date_complete'][i].strftime("%d.%m.%Y %H:%M"))
        except (ValueError, AttributeError):
            list_date_complete.append(None)
    task_pd['Дата создания'], task_pd['Срок выполнения'], task_pd['Дата выполнения'] = list_date_create, list_date_end, list_date_complete
    task_pd = task_pd.drop(task_pd.columns[[2, 3, 6]], axis=1)
    return task_pd


@logger.catch
async def get_ten_tasks(chat, page, task_list):
    if task_list == 'month':
        start_date, stop_date = await start_stop_date('month')
        tasks = session.query(Task).filter(Task.chat_id == chat.chat_id,
                                      Task.date_end >= start_date, Task.date_end <= stop_date
                                      ).order_by(Task.date_end).limit(10).offset(page*10).all()
    elif task_list == 'week':
        start_date, stop_date = await start_stop_date('week')
        tasks = session.query(Task).filter(Task.chat_id == chat.chat_id,
                                           Task.date_end >= start_date, Task.date_end < stop_date
                                           ).order_by(Task.date_end).limit(10).offset(page * 10).all()
    else:
        tasks = session.query(Task).filter(Task.chat_id == chat.chat_id,
                                           or_(Task.date_end == None, Task.date_end >= datetime.datetime.now(tz=tz)-datetime.timedelta(days=1))
                                           ).order_by(Task.date_end).limit(10).offset(page * 10).all()
    return tasks


@logger.catch
async def get_count_tasks(chat, task_list):
    if task_list == 'month':
        start_date, stop_date = await start_stop_date('month')
        count_task = session.query(Task).filter(Task.chat_id == chat.chat_id,
                                      Task.date_end >= start_date, Task.date_end <= stop_date
                                      ).count()
    elif task_list == 'week':
        start_date, stop_date = await start_stop_date('week')
        count_task = session.query(Task).filter(Task.chat_id == chat.chat_id,
                                           Task.date_end >= start_date, Task.date_end < stop_date
                                           ).count()
    else:
        count_task = session.query(Task).filter(Task.chat_id == chat.chat_id,
                                      or_(Task.date_end == None, Task.date_end >= datetime.datetime.now(tz=tz))
                                      ).count()
    return count_task


@logger.catch
async def start_stop_date(task_list):
    date_now = datetime.datetime.now()
    year, month, day, week = date_now.year, date_now.month, date_now.day, date_now.weekday()
    if task_list == 'week':
        start_date = datetime.datetime(year, month, day) - datetime.timedelta(days=week)
        stop_date = datetime.datetime(year, month, day) + datetime.timedelta(days=7 - week)
    if task_list == 'month':
        start_date = datetime.datetime(year, month, 1)
        stop_date = datetime.datetime(year, month + 1, 1)
    return start_date, stop_date


@logger.catch
async def update_task_list(user_id, task_list):
    session.query(User).filter(User.t_id == user_id).update({'task_list': task_list}, synchronize_session='fetch')
    session.commit()



@logger.catch
async def get_oldest_task(chat, start_date=0):
    oldest_task = session.query(Task).filter(Task.chat_id == chat.chat_id, Task.date_end is not None, Task.date_end >= start_date).order_by(Task.date_end).first()
    return oldest_task


async def start_stop_week(date):
    year, month, day, week = date.year, date.month, date.day, date.weekday()
    start_date = datetime.datetime(year, month, day) - datetime.timedelta(days=week)
    stop_date = datetime.datetime(year, month, day) + datetime.timedelta(days=7 - week)
    return start_date, stop_date


@logger.catch
async def get_week_tasks(chat, start_date, stop_date):
    tasks = session.query(Task).filter(Task.chat_id == chat.chat_id,
                                       Task.date_end >= start_date, Task.date_end < stop_date
                                       ).order_by(Task.date_end).all()
    return tasks
