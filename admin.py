from func.admin_func import *


@dp.callback_query_handler(cb_admins.filter())
@logger.catch
async def show_admins(call: types.CallbackQuery, callback_data: dict):
    chat = get_chat(callback_data['chat_id'])
