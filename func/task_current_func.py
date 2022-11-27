from config import *
from button import *
from func.function import *


@logger.catch
async def create_mes_task(task):
    mes = f'<b><u>{task.title}</u></b>'
    mes += f'\n<b><i>Описание:</i></b>'
    mes += f'\n{task.description}'
    mes += f'\n<b><i>Исполнители:</i></b>' if len(task.for_user) > 1 else f'\n<b><i>Исполнитель:</i></b>'
    if len(task.for_user) > 0:
        for i in task.for_user:
            mes += f'\n\t{i.user.name}'
    mes += f'\n<b><i>Добавлена:</i></b>'
    mes += f' {task.date_create.strftime("%d.%m.%Y %H:%M")}'
    mes += f'\n<b><i>Срок выполнения:</i></b>'
    if task.date_end:
        mes += f' {task.date_end.strftime("%d.%m.%Y")}'
    mes += f'\n<b><i>Выполнено:</i></b>'
    done = emojize(':check_mark_button:') if task.completed else emojize(':cross_mark:')
    mes += f' {done}'
    if task.completed:
        mes += f'\n{task.date_complete.strftime("%d.%m.%Y %H:%M")}'
    return mes


@logger.catch
async def create_kb_task(task, user_id, page=0):
    user = await get_user(user_id)
    kb_task = InlineKeyboardMarkup(row_width=4)
    btn_complete = InlineKeyboardButton(text=emojize('Готово!:check_mark_button:'),
                                        callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='compl', page=page))
    btn_show_desc = InlineKeyboardButton(text=emojize(':magnifying_glass_tilted_right::cross_mark_button::memo:'),
                                         callback_data=cb_show_comment.new(task_id=task.id))
    btn_show_comment = InlineKeyboardButton(text=emojize(':speech_balloon:'),
                                            callback_data=cb_show_desc.new(task_id=task.id))
    btn_edit_title = InlineKeyboardButton(text=emojize(':wrench::notebook:'),
                                          callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='title', page=page))
    btn_edit_desc = InlineKeyboardButton(text=emojize(':wrench::memo:'),
                                         callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='desc', page=page))
    btn_edit_date = InlineKeyboardButton(text=emojize(':wrench::tear-off_calendar:'),
                                         callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='date', page=page))
    btn_add_user = InlineKeyboardButton(text=emojize(':wrench::face_with_monocle:'),
                                        callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='add_user', page=page))
    # btn_edit_task = InlineKeyboardButton(text='Редактировать', callback_data=cb_edit_task.new(task_id=task.id))
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
    kb_task.insert(btn_show_desc).insert(btn_show_comment)
    if user.super_admin or task.user_id_create == user_id or await check_admin_chat(task.chat_id, user_id):
        kb_task.row(btn_edit_title, btn_edit_desc, btn_edit_date, btn_add_user)
    kb_task.row(btn_del_task, btn_back_tasks)
    return kb_task


# @logger.catch
# async def create_kb_edit_task(task):
#     kb_edit_task = InlineKeyboardMarkup(row_width=1)
#     btn_edit_desc = InlineKeyboardButton(text='Описание',
#                                          callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='desc'))
#     btn_edit_date = InlineKeyboardButton(text='Сроки',
#                                          callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='date'))
#     btn_add_user = InlineKeyboardButton(text=emojize(':plus:исполнитель'),
#                                         callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='add_user'))
#     btn_del_user = InlineKeyboardButton(text=emojize(':minus:исполнитель'),
#                                         callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='del_user'))
#     if task.completed:
#         btn_complete = InlineKeyboardButton(text=emojize('Не выполнено:cross_mark:'),
#                                             callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='no_compl'))
#     else:
#         btn_complete = InlineKeyboardButton(text=emojize('Выполнено:check_mark_button:'),
#                                             callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='compl'))
#     btn_back_task = InlineKeyboardButton(text=emojize(':BACK_arrow:Назад'),
#                                          callback_data=cb_type_edit_task.new(task_id=task.id, type_edit='back'))
#     kb_edit_task.row(btn_complete).row(btn_edit_desc, btn_edit_date)
#     if len(task.chat.participants) > len(task.for_user) > 0:
#         kb_edit_task.row(btn_add_user, btn_del_user)
#     elif len(task.for_user) == len(task.chat.participants):
#         kb_edit_task.row(btn_del_user)
#     else:
#         kb_edit_task.row(btn_add_user)
#     kb_edit_task.row(btn_back_task)
#     return kb_edit_task


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
async def update_date_end_task(task, date):
    session.query(Task).filter(Task.id == task.id).update({'date_edit': datetime.datetime.now(tz=tz),
                                                           'date_end': date}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def create_kb_add_user(task):
    kb_add_user = InlineKeyboardMarkup(row_width=1)
    list_user_id = await get_list_user_id_task(task)
    for part in task.chat.participants:
        if part.user.t_id not in list_user_id:
            kb_add_user.insert(InlineKeyboardButton(text=part.user.name,
                                                    callback_data=cb_add_user_task.new(task_id=task.id,
                                                                                       user_id=part.user.t_id)))
    return kb_add_user


@logger.catch
async def create_kb_del_user(task):
    kb_del_user = InlineKeyboardMarkup(row_width=1)
    list_user_id = await get_list_user_id_task(task)
    for part in task.chat.participants:
        if part.user.t_id in list_user_id:
            kb_del_user.insert(InlineKeyboardButton(text=part.user.name,
                                                    callback_data=cb_del_user_task.new(task_id=task.id,
                                                                                       user_id=part.user.t_id)))
    return kb_del_user


@logger.catch
async def get_list_user_id_task(task):
    return [i.user.t_id for i in task.for_user]


@logger.catch
async def add_user_task_db(task_id, user_id):
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
