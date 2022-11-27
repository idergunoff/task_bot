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
        user = await get_user(call.from_user.id)
        mes = emojize(f':check_mark_button: <b>{user.name}</b> сообщает о выполнении задачи:')
        mes += await create_mes_task_for_chat(task)
        await bot.send_message(task.chat_id, mes, reply_markup=kb_to_chat)
    if type_edit == 'desc':
        await TaskStates.EDIT_DESC_TASK.set()
        await state.update_data(page=callback_data['page'])
        mes = f'Описание задачи <b>{task.title}</b>:\n<i>{task.description}</i> \nОтправьте новое описание.'
        await call.message.edit_text(mes)
        await call.answer()
    if type_edit == 'title':
        await TaskStates.EDIT_TITLE_TASK.set()
        await state.update_data(page=callback_data['page'])
        mes = f'Название задачи:\n<b>{task.title}</b>\nОтправьте новое название.'
        await call.message.edit_text(mes)
        await call.answer()
    if type_edit == 'date':
        await TaskStates.EDIT_DATE_TASK.set()
        await state.update_data(page=callback_data['page'])
        calendar, step = DetailedTelegramCalendar().build()
        await call.message.edit_text(f"Выберите дату срока выполнения\nSelect {LSTEP[step]}", reply_markup=calendar)
        await call.answer()
    if type_edit == 'add_user':
        kb_add_user = await create_kb_add_user(task, int(callback_data['page']))
        await call.message.edit_text(f'Выберите исполнителя для задания <b>"{task.title}"</b>:', reply_markup=kb_add_user)
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
    if task.show_chat:
        user = await get_user(msg.from_user.id)
        mes = emojize(f'<b>{user.name}</b> изменил описание задачи:')
        mes += await create_mes_task_for_chat(task)
        await bot.send_message(task.chat_id, mes, reply_markup=kb_to_chat)
    if await check_show_chat(task):
        await bot.send_message(task.chat_id, await create_mes_task_to_chat(task), reply_markup=kb_to_chat)
        await update_show_chat(task)


@dp.message_handler(state=TaskStates.EDIT_TITLE_TASK)
@logger.catch
async def edit_title_task(msg: types.Message, state: FSMContext):
    task = await get_last_task(msg.from_user.id)
    await update_title_task(task, msg.text)
    user_data = await state.get_data()
    await state.finish()
    kb_task_edit = await create_kb_task(task, msg.from_user.id, user_data['page'])
    mes = '<i>Название задачи изменено</i>\n\n'
    mes += await create_mes_task(task)
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_task_edit)
    if task.show_chat:
        user = await get_user(msg.from_user.id)
        mes = emojize(f'<b>{user.name}</b> изменил название задачи:')
        mes += await create_mes_task_for_chat(task)
        await bot.send_message(task.chat_id, mes, reply_markup=kb_to_chat)
    if await check_show_chat(task):
        await bot.send_message(task.chat_id, await create_mes_task_to_chat(task), reply_markup=kb_to_chat)
        await update_show_chat(task)


@dp.callback_query_handler(DetailedTelegramCalendar.func(), state=TaskStates.EDIT_DATE_TASK)
@logger.catch
async def edit_date_task(call: types.CallbackQuery, state: FSMContext):
    result, key, step = DetailedTelegramCalendar(locale='ru').process(call.data)
    if not result and key:
        await call.message.edit_text(f"Select {LSTEP[step]}", reply_markup=key)
    elif result:
        user_data = await state.get_data()
        await state.finish()
        task = await get_last_task(call.from_user.id)
        await update_date_end_task(task, result)
        kb_task_edit = await create_kb_task(task, call.from_user.id, user_data['page'])
        mes = '<i>Срок выполнения изменён</i>\n\n'
        mes += await create_mes_task(task)
        await call.message.edit_text(mes, reply_markup=kb_task_edit)
        await call.answer()
        if task.show_chat:
            user = await get_user(call.from_user.id)
            mes = emojize(f'<b>{user.name}</b> изменил сроки выполнения задачи:')
            mes += await create_mes_task_for_chat(task)
            await bot.send_message(task.chat_id, mes, reply_markup=kb_to_chat)
        if await check_show_chat(task):
            await bot.send_message(task.chat_id, await create_mes_task_to_chat(task), reply_markup=kb_to_chat)
            await update_show_chat(task)


@dp.callback_query_handler(cb_add_user_task.filter())
@logger.catch
async def add_user_task(call: types.CallbackQuery, callback_data: dict):
    task = await get_task(callback_data['task_id'])
    await add_user_task_db(task.id, callback_data['user_id'])
    kb_task_edit = await create_kb_task(task, call.from_user.id, callback_data['page'])
    mes = '<i>Исполнитель выбран</i>\n\n'
    mes += await create_mes_task(task)
    await call.message.edit_text(mes, reply_markup=kb_task_edit)
    await call.answer()
    if task.show_chat:
        user = await get_user(call.from_user.id)
        mes = emojize(f'<b>{user.name}</b> изменил исполнителя задачи:')
        mes += await create_mes_task_for_chat(task)
        await bot.send_message(task.chat_id, mes, reply_markup=kb_to_chat)
    if await check_show_chat(task):
        await bot.send_message(task.chat_id, await create_mes_task_to_chat(task), reply_markup=kb_to_chat)
        await update_show_chat(task)


@dp.callback_query_handler(cb_show_desc.filter())
@logger.catch
async def show_desc_task(call: types.CallbackQuery, callback_data: dict):
    task = await get_task(callback_data['task_id'])
    mes = await create_mes_task(task, True)
    kb_task = await create_kb_task(task, call.from_user.id, callback_data['page'], True)
    await call.message.edit_text(mes, reply_markup=kb_task)
    await call.answer()


@dp.callback_query_handler(cb_not_show_desc.filter())
@logger.catch
async def show_not_desc_task(call: types.CallbackQuery, callback_data: dict):
    task = await get_task(callback_data['task_id'])
    mes = await create_mes_task(task)
    kb_task = await create_kb_task(task, call.from_user.id, callback_data['page'])
    await call.message.edit_text(mes, reply_markup=kb_task)
    await call.answer()