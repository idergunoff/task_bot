from func.admin_func import *
from func.task_list_func import create_show_tasks_kb, create_show_tasks_mes


@dp.callback_query_handler(cb_admins.filter())
@logger.catch
async def show_admins(call: types.CallbackQuery, callback_data: dict):
    chat = await get_chat(callback_data['chat_id'])
    mes = await create_mes_admins(chat)
    kb_admin = await create_kb_admins(chat)
    await call.message.edit_text(mes, reply_markup=kb_admin)
    await call.answer()


@dp.callback_query_handler(cb_back_task_admin.filter())
@logger.catch
async def back_task_admin(call: types.CallbackQuery, callback_data: dict):
    user = await get_user(call.from_user.id)
    chat = await get_chat(callback_data['chat_id'])
    kb_task = await create_show_tasks_kb(chat, 0, task_list=user.task_list)
    if user.super_admin:
        kb_task.insert(InlineKeyboardButton('Админы',
                                            callback_data=cb_admins.new(chat_id=chat.chat_id)))
    mes = await create_show_tasks_mes(chat, call.from_user.id, 0, task_list=user.task_list)
    await call.message.edit_text(mes, reply_markup=kb_task)
    await call.answer()


@dp.callback_query_handler(cb_add_admin.filter())
@logger.catch
async def add_admin(call: types.CallbackQuery, callback_data: dict):
    chat = await get_chat(callback_data['chat_id'])
    kb_add_admin = await create_kb_add_admins(chat)
    await call.message.edit_text(f'Выберите админа чата <b>{chat.title}</b> из пользователей:', reply_markup=kb_add_admin)
    await call.answer()


@dp.callback_query_handler(cb_del_admin.filter())
@logger.catch
async def del_admin(call: types.CallbackQuery, callback_data: dict):
    chat = await get_chat(callback_data['chat_id'])
    kb_del_admin = await create_kb_del_admins(chat)
    await call.message.edit_text(f'Выберите пользователя чата <b>{chat.title}</b> для удаления из админов:', reply_markup=kb_del_admin)
    await call.answer()


@dp.callback_query_handler(cb_back_admins.filter())
@logger.catch
async def back_admin(call: types.CallbackQuery, callback_data: dict):
    await show_admins(call, callback_data)


@dp.callback_query_handler(cb_add_user_admin.filter())
@logger.catch
async def add_user_admin(call: types.CallbackQuery, callback_data: dict):
    await add_user_admin_db(callback_data['chat_id'], callback_data['user_id'])
    await show_admins(call, callback_data)


@dp.callback_query_handler(cb_del_user_admin.filter())
@logger.catch
async def del_user_admin(call: types.CallbackQuery, callback_data: dict):
    await del_user_admin_db(callback_data['chat_id'], callback_data['user_id'])
    await show_admins(call, callback_data)