import openpyxl
from openpyxl.styles import PatternFill, Color

from func.task_list_func import *


@dp.message_handler(text='Задачи')
@logger.catch
async def push_task(msg: types.Message):
    logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH TASKS')
    user = await get_user(msg.from_user.id)
    if user:
        if len(user.participants) > 1:
            kb_chat = await create_show_chat_for_tasks_kb(user)
            mes = emojize('Выберите чат:')
            await bot.send_message(user.t_id, mes, reply_markup=kb_chat)
        elif len(user.participants) < 1:
            await msg.reply('Не однин ваш чат не зарегистрирован в "TaskBot"')
        else:
            kb_task = await create_show_tasks_kb(user.participants[0].chat, task_list=user.task_list)
            if user.super_admin:
                kb_task.insert(InlineKeyboardButton('Админы', callback_data=cb_admins.new(chat_id=user.participants[0].chat.chat_id)))
            mes = await create_show_tasks_mes(user.participants[0].chat, msg.from_user.id, task_list=user.task_list)
            await bot.send_message(msg.from_user.id, mes, reply_markup=kb_task)
    else:
        await msg.reply('Не однин ваш чат не зарегистрирован в "TaskBot"')


@dp.callback_query_handler(cb_chat_task.filter())
@logger.catch
async def choose_chat_for_task(call: types.CallbackQuery, callback_data: dict):
    user = await get_user(call.from_user.id)
    chat = await get_chat(callback_data['chat_id'])
    kb_task = await create_show_tasks_kb(chat, task_list=user.task_list)
    if user.super_admin:
        kb_task.insert(InlineKeyboardButton('Админы',
                       callback_data=cb_admins.new(chat_id=chat.chat_id)))
    mes = await create_show_tasks_mes(chat, call.from_user.id, task_list=user.task_list)
    await call.message.edit_text(emojize(mes), reply_markup=kb_task)
    await call.answer()


@dp.callback_query_handler(cb_new_task.filter())
@logger.catch
async def new_task(call: types.CallbackQuery, callback_data: dict):
    logger.info(f'USER "{call.from_user.id} - {await get_username_call(call)}" PUSH new_task')
    await add_new_task(callback_data['chat_id'], call.from_user.id)
    logger.success(f'USER "{call.from_user.id} - {await get_username_call(call)}" CREATE new_task')
    await TaskStates.NEW_TASK.set()
    await bot.send_message(call.from_user.id, 'Отправь название задачи.')
    await call.answer()


@dp.callback_query_handler(text='back_chat_task')
@logger.catch
async def back_chat_for_task(call: types.CallbackQuery):
    kb_chat = await create_show_chat_for_tasks_kb(await get_user(call.from_user.id))
    await call.message.edit_text('Выберите чат:', reply_markup=kb_chat)
    await call.answer()


@dp.callback_query_handler(cb_back_task.filter())
@logger.catch
async def back_task(call: types.CallbackQuery, callback_data: dict):
    user = await get_user(call.from_user.id)
    chat = await get_chat(callback_data['chat_id'])
    kb_task = await create_show_tasks_kb(chat, int(callback_data['page']), task_list=user.task_list)
    if user.super_admin:
        kb_task.insert(InlineKeyboardButton('Админы',
                       callback_data=cb_admins.new(chat_id=chat.chat_id)))
    mes = await create_show_tasks_mes(chat, call.from_user.id, int(callback_data['page']), task_list=user.task_list)
    await call.message.edit_text(mes, reply_markup=kb_task)
    await call.answer()


@dp.callback_query_handler(cb_page_list_task.filter())
@logger.catch
async def page_task(call: types.CallbackQuery, callback_data: dict):
    user = await get_user(call.from_user.id)
    chat = await get_chat(callback_data['chat_id'])
    kb_task = await create_show_tasks_kb(chat, page=int(callback_data['page']), task_list=user.task_list)
    if user.super_admin:
        kb_task.insert(InlineKeyboardButton('Админы',
                       callback_data=cb_admins.new(chat_id=chat.chat_id)))
    mes = await create_show_tasks_mes(chat, call.from_user.id, page=int(callback_data['page']), task_list=user.task_list)
    await call.message.edit_text(mes, reply_markup=kb_task)
    await call.answer()


@dp.callback_query_handler(cb_del_task.filter())
@logger.catch
async def del_task(call: types.CallbackQuery, callback_data: dict):
    user = await get_user(call.from_user.id)
    task = await get_task(callback_data['task_id'])
    chat, title = task.chat, task.title
    await del_task_by_id(callback_data['task_id'])
    kb_task = await create_show_tasks_kb(chat, task_list=user.task_list)
    if user.super_admin:
        kb_task.insert(InlineKeyboardButton('Админы',
                       callback_data=cb_admins.new(chat_id=chat.chat_id)))
    mes = emojize(f'Задача <b>{title}</b> удалена.\n')
    mes += await create_show_tasks_mes(chat, call.from_user.id, task_list=user.task_list)
    await call.message.edit_text(emojize(mes), reply_markup=kb_task)
    await call.answer()
    mes = f'<b>{user.name}</b> удалил задачу <u><b>{title}</b></u>'
    await bot.send_message(chat.chat_id, mes, reply_markup=kb_to_chat)


@dp.callback_query_handler(cb_week_tasks.filter())
@logger.catch
async def week_task(call: types.CallbackQuery, callback_data: dict):
    await update_task_list(call.from_user.id, 'week')
    await choose_chat_for_task(call=call, callback_data=callback_data)
    await call.answer()


@dp.callback_query_handler(cb_month_tasks.filter())
@logger.catch
async def month_task(call: types.CallbackQuery, callback_data: dict):
    await update_task_list(call.from_user.id, 'month')
    await choose_chat_for_task(call=call, callback_data=callback_data)
    await call.answer()


@dp.callback_query_handler(cb_all_tasks.filter())
@logger.catch
async def all_task(call: types.CallbackQuery, callback_data: dict):
    await update_task_list(call.from_user.id, 'all')
    await choose_chat_for_task(call=call, callback_data=callback_data)
    await call.answer()


@dp.callback_query_handler(cb_excel_tasks.filter())
@logger.catch
async def excel_task(call: types.CallbackQuery, callback_data: dict):
    task_pd = await get_excel_task(callback_data['chat_id'])
    task_pd.to_excel('task.xlsx')
    wb = openpyxl.load_workbook('task.xlsx')
    sheet = wb.active
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:  # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column].width = adjusted_width
    # cell.fill = PatternFill("solid", fgColor="DDDDDD")
    rows = sheet.max_row
    cols = sheet.max_column

    for i in range(1, rows + 1):
        if sheet.cell(row=i, column=5).value == 'Выполнено':
            for j in range(1, cols + 1):
                sheet.cell(row=i, column=j).fill = PatternFill("solid", fgColor="98FB98")
        else:
            for j in range(1, cols + 1):
                sheet.cell(row=i, column=j).fill = PatternFill("solid", fgColor="F08080")
    wb.save('task.xlsx')
    await bot.send_document(call.from_user.id, open('task.xlsx', 'rb'))
    await call.answer()