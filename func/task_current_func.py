from config import *
from button import *
from func.function import *


@logger.catch
async def add_new_task(chat_id, user_id):
    new_task = Task(
        chat_id=chat_id,
        user_id_create=user_id,
        user_id_edit=user_id,
        date_create=datetime.datetime.now(tz=tz),
        date_edit=datetime.datetime.now(tz=tz)
    )
    session.add(new_task)
    session.commit()


@logger.catch
async def add_new_task_cmd(chat_id, user_id, task_data, for_user_id):
    new_task = Task(
        chat_id=chat_id,
        user_id_create=user_id,
        user_id_edit=user_id,
        date_create=datetime.datetime.now(tz=tz),
        date_edit=datetime.datetime.now(tz=tz),
        title=task_data['title'],
        description=task_data['description'],
        date_end=task_data['date_end']
    )
    session.add(new_task)
    session.commit()
    new_task_for_user = TaskForUser(
        task_id=new_task.id,
        user_id=for_user_id
    )
    session.add(new_task_for_user)
    session.commit()
    return new_task


@logger.catch
async def add_new_task_bot(user_id, task_data, for_user_id):
    new_task = Task(
        chat_id=task_data['chat_id_bot'],
        user_id_create=user_id,
        user_id_edit=user_id,
        date_create=datetime.datetime.now(tz=tz),
        date_edit=datetime.datetime.now(tz=tz),
        title=task_data['title_bot'],
        description=task_data['description_bot'],
        date_end=task_data['date_end_bot']
    )
    session.add(new_task)
    session.commit()
    new_task_for_user = TaskForUser(
        task_id=new_task.id,
        user_id=for_user_id
    )
    session.add(new_task_for_user)
    session.commit()
    return new_task


@logger.catch
async def create_mes_task(task, description=False):
    mes = f'Выполнено:'
    done = emojize(':check_mark_button:') if task.completed else emojize(':cross_mark:')
    mes += f' {done}'
    mes += f'\n<b><u>{task.title}</u></b>'
    mes += f'\nКому назначено:'
    if len(task.for_user) > 0:
        mes += f' <b><i>{task.for_user[0].user.name}</i></b>'
    mes += f'\nСрок:'
    if task.date_end:
        mes += f' <b><i>{task.date_end.strftime("%d.%m.%Y")}</i></b>'
    if description:
        mes += f'\nОписание:'
        mes += f'\n<b><i>{task.description}</i></b>'
    return mes


@logger.catch
async def create_kb_task(task, user_id, page=0, description=False):
    user = await get_user(user_id)
    kb_task = InlineKeyboardMarkup(row_width=4)
    btn_complete = InlineKeyboardButton(text=emojize('Готово!:check_mark_button:'),
                                        callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='compl', page=page))
    if not description:
        btn_show_desc = InlineKeyboardButton(text=emojize(':magnifying_glass_tilted_right:Описание'),
                                             callback_data=cb_show_desc.new(task_id=task.id, page=page))
    else:
        btn_show_desc = InlineKeyboardButton(text=emojize(':cross_mark_button:Описание'),
                                             callback_data=cb_not_show_desc.new(task_id=task.id, page=page))
    btn_edit_title = InlineKeyboardButton(text=emojize(':wrench:Название'),
                                          callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='title', page=page))
    btn_edit_desc = InlineKeyboardButton(text=emojize(':wrench:Описание'),
                                         callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='desc', page=page))
    btn_edit_date = InlineKeyboardButton(text=emojize(':wrench:Срок выполнения'),
                                         callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='date', page=page))
    btn_add_user = InlineKeyboardButton(text=emojize(':wrench:Кому назначено'),
                                        callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='add_user', page=page))
    btn_del_task = InlineKeyboardButton(text=emojize(':wastebasket:'), callback_data=cb_del_task.new(task_id=task.id))
    btn_back_tasks = InlineKeyboardButton(text=emojize(':BACK_arrow:Назад'),
                                          callback_data=cb_back_task.new(chat_id=task.chat_id, page=page))
    if len(task.for_user) > 0:
        if user.super_admin or task.user_id_create == user_id or await check_admin_chat(task.chat_id, user_id) or \
                user_id == task.for_user[0].user_id:
            if not task.completed:
                kb_task.insert(btn_complete)
    else:
        if user.super_admin or task.user_id_create == user_id or await check_admin_chat(task.chat_id, user_id):
            if not task.completed:
                kb_task.insert(btn_complete)
    kb_task.insert(btn_show_desc)
    if user.super_admin or task.user_id_create == user_id or await check_admin_chat(task.chat_id, user_id):
        if not task.completed:
            kb_task.row(btn_edit_title, btn_edit_desc).row(btn_edit_date, btn_add_user)
    kb_task.row(btn_back_tasks)
    if user.super_admin or task.user_id_create == user_id or await check_admin_chat(task.chat_id, user_id):
        kb_task.insert(btn_del_task)
    return kb_task


@logger.catch
async def edit_complete(task, completed):
    session.query(Task).filter(Task.id == task.id).update({'completed': completed, 'date_complete':
        datetime.datetime.now(tz=tz), 'date_edit': datetime.datetime.now(tz=tz)}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_date_edit(task, user_id):
    session.query(Task).filter(Task.id == task.id).update({'date_edit': datetime.datetime.now(tz=tz),
                                                           'user_id_edit': user_id}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_desc_task(task, text):
    session.query(Task).filter(Task.id == task.id).update({'date_edit': datetime.datetime.now(tz=tz),
                                                           'description': text}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_title_task(task, text):
    session.query(Task).filter(Task.id == task.id).update({'date_edit': datetime.datetime.now(tz=tz),
                                                           'title': text}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def update_date_end_task(task, date):
    session.query(Task).filter(Task.id == task.id).update({'date_edit': datetime.datetime.now(tz=tz),
                                                           'date_end': date}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def create_kb_add_user(task, page):
    kb_add_user = InlineKeyboardMarkup(row_width=1)
    list_user_id = await get_list_user_id_task(task)
    for part in task.chat.participants:
        if part.user.t_id not in list_user_id:
            kb_add_user.insert(InlineKeyboardButton(text=part.user.name,
                                                    callback_data=cb_add_user_task.new(task_id=task.id,
                                                                                       user_id=part.user.t_id,
                                                                                       page=page)))
    return kb_add_user


@logger.catch
async def create_kb_new_task_user(chat_id):
    kb_new_task_user = InlineKeyboardMarkup(row_width=1)
    chat = await get_chat(chat_id)
    for part in chat.participants:
        kb_new_task_user.insert(InlineKeyboardButton(text=part.user.name,
                                                    callback_data=cb_new_task_user.new(user_id=part.user.t_id)))
        kb_new_task_user.insert(btn_cancel)
    return kb_new_task_user


@logger.catch
async def get_list_user_id_task(task):
    return [i.user.t_id for i in task.for_user]


@logger.catch
async def add_user_task_db(task_id, user_id):
    session.query(TaskForUser).filter(TaskForUser.task_id == task_id).delete()
    new_task_for_user = TaskForUser(task_id=task_id, user_id=user_id)
    session.add(new_task_for_user)
    session.commit()


@logger.catch
async def del_user_task_db(task_id, user_id):
    session.query(TaskForUser).filter(TaskForUser.task_id == task_id, TaskForUser.user_id == user_id).delete()
    session.commit()


@logger.catch
async def add_title_task(task, title):
    session.query(Task).filter(Task.id == task.id).update({'title': title, 'date_edit': datetime.datetime.now(tz=tz)},
                                                          synchronize_session='fetch')
    session.commit()


@logger.catch
async def check_show_chat(task):
    if task.show_chat:
        return False
    else:
        if task.description and task.date_end and len(task.for_user) > 0:
            return True
        else:
            return False


@logger.catch
async def create_mes_task_to_chat(task):
    mes = f'<b><u>ДОБАВЛЕНО ({task.id})</u></b>'
    mes += await create_mes_task_for_chat(task)
    return mes


@logger.catch
async def create_mes_task_for_chat(task):
    circle = ':green_circle:'*12
    mes = f'\nкому - <b>{task.for_user[0].user.name}</b>{task.user_create.name}'
    mes += f'\nсрок - <b>{task.date_end.strftime("%d.%m.%Y")}</b>'
    mes += f'\nкто - <b>{task.user_create.name}</b>'
    mes += emojize(f'\n{circle}\n{task.description}')
    return mes


@logger.catch
async def update_show_chat(task):
    session.query(Task).filter(Task.id == task.id).update({'show_chat': True}, synchronize_session='fetch')
    session.commit()
