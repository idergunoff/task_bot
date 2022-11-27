from button import *
from func.task_current_func import *


@dp.message_handler(state=TaskStates.NEW_TASK)
@logger.catch
async def add_task(msg: types.Message, state: FSMContext):
    await state.finish()
    task = await get_last_task(msg.from_user.id)
    await add_title_task(task, msg.text)
    logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" ADD title task')
    mes = emojize(f'Задача <b>{msg.text}</b> добавлена.')
    await bot.send_message(msg.from_user.id, mes)
    mes = await create_mes_task(task)
    kb_task = await create_kb_task(task, msg.from_user.id)
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_task)


@dp.callback_query_handler(cb_task.filter())
@logger.catch
async def show_task(call: types.CallbackQuery, callback_data: dict):
    task = await get_task(callback_data['task_id'])
    mes = await create_mes_task(task)
    kb_task = await create_kb_task(task, call.from_user.id, callback_data['page'])
    await call.message.edit_text(mes, reply_markup=kb_task)
    await call.answer()


# @dp.callback_query_handler(cb_edit_task.filter())
# @logger.catch
# async def edit_task(call: types.CallbackQuery, callback_data: dict):
#     task = await get_task(callback_data['task_id'])
#     kb_task_edit = await create_kb_edit_task(task)
#     mes = await create_mes_task(task)
#     mes += '\n\n<b><i><u>Редактирование</u></i></b>'
#     await call.message.edit_text(mes, reply_markup=kb_task_edit)
#     await call.answer()


@dp.callback_query_handler(cb_type_edit_task.filter())
@logger.catch
async def type_edit_task(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    task = await get_task(callback_data['task_id'])
    type_edit = callback_data['type_edit']
    await update_date_edit(task, call.from_user.id)
    if type_edit == 'compl':
        await edit_complete(task, True)
        kb_task_edit = await create_kb_task(task, call.from_user.id, int(callback_data['page']))
        mes = await create_mes_task(task)
        await call.message.edit_text(mes, reply_markup=kb_task_edit)
        await call.answer()
    if type_edit == 'desc':
        await TaskStates.EDIT_DESC_TASK.set()
        await state.update_data(page=callback_data['page'])
        mes = f'Описание задачи <b>{task.title}</b>:\n<i>{task.description}</i> \nОтправьте новое описание.'
        await call.message.edit_text(mes)
        await call.answer()
    if type_edit == 'date':
        await TaskStates.EDIT_DATE_TASK.set()
        calendar, step = DetailedTelegramCalendar().build()
        await call.message.edit_text(f"Выберите сроки выполнения\nSelect {LSTEP[step]}", reply_markup=calendar)
        await call.answer()
    if type_edit == 'add_user':
        kb_add_user = await create_kb_add_user(task)
        await call.message.edit_text(f'Выберите исполнителя для задания <b>"{task.title}"</b>:', reply_markup=kb_add_user)
        await call.answer()
    if type_edit == 'del_user':
        kb_del_user = await create_kb_del_user(task)
        await call.message.edit_text(f'Выберите пользователя для удаления из исполнителей задания <b>"{task.title}"</b>', reply_markup=kb_del_user)
        await call.answer()
    if type_edit == 'back':
        mes = await create_mes_task(task)
        kb_task = await create_kb_task(task)
        await call.message.edit_text(mes, reply_markup=kb_task)
        await call.answer()


@dp.message_handler(state=TaskStates.EDIT_DESC_TASK)
@logger.catch
async def edit_desc_task(msg: types.Message, state: FSMContext):
    task = await get_last_task(msg.from_user.id)
    await update_desc_task(task, msg.text)
    user_data = await state.get_data()
    await state.finish()
    kb_task_edit = await create_kb_task(task, msg.from_user.id, user_data['page'])
    mes = '<i>Описание изменено</i>\n\n'
    mes += await create_mes_task(task)
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_task_edit)


@dp.callback_query_handler(DetailedTelegramCalendar.func(), state=TaskStates.EDIT_DATE_TASK)
@logger.catch
async def edit_date_task(call: types.CallbackQuery, state: FSMContext):
    result, key, step = DetailedTelegramCalendar(locale='ru').process(call.data)
    if not result and key:
        await call.message.edit_text(f"Select {LSTEP[step]}", reply_markup=key)
    elif result:
        await state.finish()
        task = await get_last_task(call.from_user.id)
        await update_date_end_task(task, result)
        kb_task_edit = await create_kb_edit_task(task)
        mes = '<i>Срок выполнения изменён</i>\n\n'
        mes += await create_mes_task(task)
        mes += '\n\n<b><i><u>Редактирование</u></i></b>'
        await call.message.edit_text(mes, reply_markup=kb_task_edit)
        await call.answer()


@dp.callback_query_handler(cb_add_user_task.filter())
@logger.catch
async def add_user_task(call: types.CallbackQuery, callback_data: dict):
    task = await get_task(callback_data['task_id'])
    await add_user_task_db(task.id, callback_data['user_id'])
    kb_task_edit = await create_kb_edit_task(task)
    mes = '<i>Исполнитель добавлен</i>\n\n'
    mes += await create_mes_task(task)
    mes += '\n\n<b><i><u>Редактирование</u></i></b>'
    await call.message.edit_text(mes, reply_markup=kb_task_edit)
    await call.answer()


@dp.callback_query_handler(cb_del_user_task.filter())
@logger.catch
async def del_user_task(call: types.CallbackQuery, callback_data: dict):
    task = await get_task(callback_data['task_id'])
    await del_user_task_db(task.id, callback_data['user_id'])
    kb_task_edit = await create_kb_edit_task(task)
    mes = '<i>Исполнитель удалён</i>\n\n'
    mes += await create_mes_task(task)
    mes += '\n\n<b><i><u>Редактирование</u></i></b>'
    await call.message.edit_text(mes, reply_markup=kb_task_edit)
    await call.answer()