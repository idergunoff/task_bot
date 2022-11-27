import datetime

from config import *
from button import *
from func.function import *


@logger.catch
async def create_show_tasks_kb(chat, page=0):
    tasks = await get_ten_tasks(chat, page)
    kb_task = InlineKeyboardMarkup(row_width=5)
    for n, task in enumerate(tasks):
        kb_task.insert(InlineKeyboardButton(text=f'{str(n + page * 10 + 1)}', callback_data=cb_task.new(task_id=task.id, page=page)))
    if len(tasks) < 10:
        for _ in range(10 - len(tasks)):
            kb_task.insert(InlineKeyboardButton(text='-', callback_data='not_button'))
    btn_new_task = InlineKeyboardButton(emojize(':memo:Новая задача'), callback_data=cb_new_task.new(chat_id=chat.chat_id))
    btn_excel_task = InlineKeyboardButton(text='Выгрузить Excel', callback_data=cb_excel_tasks.new(chat_id=chat.chat_id))
    if page > 0:
        kb_task.row(InlineKeyboardButton(text='<<', callback_data=cb_page_list_task.new(chat_id=chat.chat_id, page=page - 1)))
    kb_task.insert(btn_new_task)
    if page < (await get_count_tasks(chat) - 1) // 10:
        kb_task.insert(InlineKeyboardButton(text='>>', callback_data=cb_page_list_task.new(chat_id=chat.chat_id, page=page + 1)))
    kb_task.row(btn_excel_task).row(btn_back_chat_task)
    return kb_task


@logger.catch
async def create_show_tasks_mes(chat, user_id, page=0):
    tasks = await get_ten_tasks(chat, page)
    mes = emojize(f'<u>Выберите задачу чата <b>{chat.title}</b>:({await get_count_tasks(chat)})</u>')
    for n, task in enumerate(tasks):
        warning = ':warning:' if not task.description or not task.date_end or len(task.for_user) == 0 else ''
        complete = ':check_mark_button:' if task.completed else ':cross_mark:'
        my_task = ''
        if len(task.for_user) > 0:
            my_task = ':face_with_monocle:' if user_id == task.for_user[0].user_id else ''
        mes += emojize(f'\n{complete} <b>{str(n + page * 10 + 1)}.</b>{my_task} {task.title} {warning}')
    return mes


@logger.catch
async def create_show_chat_for_tasks_kb(user):
    kb_chat = InlineKeyboardMarkup(row_width=1)
    for part in user.participants:
        kb_chat.insert(InlineKeyboardButton(text=part.chat.title, callback_data=cb_chat_task.new(chat_id=part.chat.chat_id)))
    return kb_chat


@logger.catch
async def add_new_task(chat_id, user_id):
    new_task = Task(chat_id=chat_id, user_id_create=user_id, user_id_edit=user_id, date_create=datetime.datetime.now(tz=tz),
                    date_edit=datetime.datetime.now(tz=tz))
    session.add(new_task)
    session.commit()


@logger.catch
async def del_task_by_id(task_id):
    session.query(Task).filter(Task.id == task_id).delete()
    session.query(TaskForUser).filter(TaskForUser.task_id == task_id).delete()
    session.commit()


@logger.catch
async def get_excel_task(chat_id):
    task_pd = pd.read_sql(session.query(Task).filter(Task.chat_id == chat_id).statement, engine)
    task_pd = task_pd.drop(task_pd.columns[[0, 1, 5, 8]], axis=1)
    task_pd = task_pd.rename(columns={'title': 'Задача', 'description': 'Описание', 'date_create': 'Дата создания',
                                      'date_end': 'Срок выполнения', 'user_id_create': 'Автор задачи',
                                      'completed': 'Выполнено', 'date_complete': 'Дата выполнения'})
    for i in range(len(task_pd['Автор задачи'])):
        user = await get_user(int(task_pd['Автор задачи'][i]))
        task_pd['Автор задачи'][i] = user.name
    return task_pd


@logger.catch
async def get_ten_tasks(chat, page):
    return session.query(Task).filter(Task.chat_id == chat.chat_id,
                                      or_(Task.date_end == None, Task.date_end >= datetime.datetime.now(tz=tz))
                                      ).order_by(Task.date_end).limit(10).offset(page*10).all()


@logger.catch
async def get_count_tasks(chat):
    return session.query(Task).filter(Task.chat_id == chat.chat_id,
                                      or_(Task.date_end == None, Task.date_end >= datetime.datetime.now(tz=tz))
                                      ).count()
