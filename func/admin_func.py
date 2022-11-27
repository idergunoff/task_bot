from config import *
from button import *
from func.function import *


@logger.catch
async def create_mes_admins(chat):
    mes = f'Администраторы чата <b>{chat.title}</b>:'
    for n, i in enumerate(session.query(Participant).filter(Participant.chat_id == chat.chat_id, Participant.admin == True).all()):
        mes += f'\n{str(n + 1)}. {i.user.name}'
    return mes


@logger.catch
async def create_kb_admins(chat):
    kb_admin = InlineKeyboardMarkup(row_width=2)
    btn_add_admin = InlineKeyboardButton('Назначить', callback_data=cb_add_admin.new(chat_id=chat.chat_id))
    btn_del_admin = InlineKeyboardButton('Убрать', callback_data=cb_del_admin.new(chat_id=chat.chat_id))
    btn_back_task_admin = InlineKeyboardButton('Выйти из админ-меню', callback_data=cb_back_task_admin.new(chat_id=chat.chat_id))
    kb_admin.row(btn_add_admin, btn_del_admin).row(btn_back_task_admin)
    return kb_admin


@logger.catch
async def create_kb_add_admins(chat):
    kb_add_admin = InlineKeyboardMarkup(row_width=1)
    for i in session.query(Participant).filter(Participant.chat_id == chat.chat_id, Participant.admin == False).all():
         kb_add_admin.insert(InlineKeyboardButton(f'{i.user.name}', callback_data = cb_add_user_admin.new(chat_id=chat.chat_id, user_id=i.user.t_id)))
    btn_back_admin = InlineKeyboardButton('Отмена', callback_data=cb_back_admins.new(chat_id=chat.chat_id))
    kb_add_admin.insert(btn_back_admin)
    return kb_add_admin


@logger.catch
async def create_kb_del_admins(chat):
    kb_del_admin = InlineKeyboardMarkup(row_width=1)
    for i in session.query(Participant).filter(Participant.chat_id == chat.chat_id, Participant.admin == True).all():
         kb_del_admin.insert(InlineKeyboardButton(f'{i.user.name}', callback_data = cb_del_user_admin.new(chat_id=chat.chat_id, user_id=i.user.t_id)))
    btn_back_admin = InlineKeyboardButton('Отмена', callback_data=cb_back_admins.new(chat_id=chat.chat_id))
    kb_del_admin.insert(btn_back_admin)
    return kb_del_admin


@logger.catch
async def add_user_admin_db(chat_id, user_id):
    session.query(Participant).filter(Participant.chat_id == chat_id, Participant.user_id == user_id).update(
        {'admin': True}, synchronize_session='fetch')
    session.commit()


@logger.catch
async def del_user_admin_db(chat_id, user_id):
    session.query(Participant).filter(Participant.chat_id == chat_id, Participant.user_id == user_id).update(
        {'admin': False}, synchronize_session='fetch')
    session.commit()
