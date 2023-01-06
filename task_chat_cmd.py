from button import *
from func.task_current_func import *
from func.task_list_func import *


@dp.message_handler(commands='cancel', state=[
    TaskStates.NEW_TASK_TITLE,
    TaskStates.NEW_TASK_DESC,
    TaskStates.NEW_TASK_DATE,
    TaskStates.DELETE_TASK,
    TaskStates.DONE_TASK
])
@logger.catch
async def cancel_new_task(msg: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(msg.chat.id, 'Отмена!')
    logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" CANCEL')


###################
### Регистрация ###
###################
@dp.message_handler(commands=['reg'])
@logger.catch
async def registration(msg: types.Message):
    logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" COMMAND REG')
    if msg.chat.id == msg.from_user.id:
        mes = 'Данная команда должна использоваться в чате'
        await bot.send_message(msg.chat.id, mes)
        logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" COMMAND REG IN BOT')
    else:
        if await check_chat(msg.chat.id, msg.chat.title):
            mes = f'Чат "{msg.chat.title}" добален в "TaskBot".'
            await bot.send_message(msg.chat.id, mes)
            logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" REG CHAT "{msg.chat.title}"')
        if await check_user(msg.from_user.id, msg):
            mes = f'Пользователь "{await get_username_msg(msg)}" добален в "TaskBot".'
            await bot.send_message(msg.chat.id, mes)
            logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" REG')
        if await check_user_in_chat(msg.chat.id, msg.from_user.id):
            mes = f'Пользователь "{await get_username_msg(msg)}" зарегистрирован в чате "{msg.chat.title}" в "TaskBot".'
            await bot.send_message(msg.chat.id, mes)
            logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" REG TO CHAT "{msg.chat.title}"')

    # mes = emojize(msg.from_user.first_name + ", добро пожаловать в бот \n:waving_hand:")
    # await bot.send_message(msg.from_user.id, mes)
    # logger.info(f'Push "/start" - user "{msg.from_user.id} - {msg.from_user.username}"')
    # # await check_chat_participant(-1001789257723)
    # # await check_chat(-1001789257723)
    # a = await bot.get_chat_member(-1001789257723, 5468555552)
    # print(a.status)


@dp.message_handler(commands=['new'])
@logger.catch
async def new_task_cmd(msg: types.Message, state: FSMContext):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.\nДля '
                     'добавления новой задачи в боте сначала выберите чат, а потом нажмите кнопку "Добавить задачу"')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH new_task_cmd IN BOT')
    else:
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH new_task_cmd')
        await registration(msg=msg)
        await TaskStates.NEW_TASK_TITLE.set()
        await state.update_data(user_id_create=msg.from_user.id, chat_id=msg.chat.id)
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, отправь название задачи.\n '
                                            f'Для отмены добавления задачи отправь /cancel')


@dp.message_handler(state=TaskStates.NEW_TASK_TITLE)
@logger.catch
async def new_task_title(msg: types.Message, state: FSMContext):
    task_data = await state.get_data()
    if msg.from_user.id == task_data['user_id_create']:
        await TaskStates.NEW_TASK_DESC.set()
        await state.update_data(title=msg.text)
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, отправь описание задачи. '
                                            f'Для отмены добавления задачи отправь /cancel')
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND title')


@dp.message_handler(state=TaskStates.NEW_TASK_DESC)
@logger.catch
async def new_task_desc(msg: types.Message, state: FSMContext):
    task_data = await state.get_data()
    if msg.from_user.id == task_data['user_id_create']:
        await TaskStates.NEW_TASK_DATE.set()
        await state.update_data(description=msg.text)
        await bot.send_message(
            msg.chat.id,
            f'<b>{await get_username_msg(msg)}</b>, отправь срок выполнения задачи в формате "<i>01.01.2023</i>". '
            f'Для отмены добавления задачи отправь /cancel'
        )
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND description')


@dp.message_handler(state=TaskStates.NEW_TASK_DATE)
@logger.catch
async def new_task_date(msg: types.Message, state: FSMContext):
    task_data = await state.get_data()
    if msg.from_user.id == task_data['user_id_create']:
        try:
            date_end = datetime.datetime.strptime(msg.text, '%d.%m.%Y')
        except ValueError:
            await bot.send_message(
                msg.chat.id,
                emojize(f':warning:Внимание!!!:warning:\nНеправильный формат даты!\n'
                f'<b>{await get_username_msg(msg)}</b>, отправь срок выполнения задачи в формате "<i>01.01.2023</i>". '
                        f'Для отмены добавления задачи отправь /cancel')
            )
            logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND error format date')
            return
        if date_end.timestamp() < datetime.datetime.now(tz=tz).timestamp():
            await bot.send_message(
                msg.chat.id,
                emojize(f':warning:Внимание!!!:warning:\nВыбранная дата уже прошла, выберите дату в будущем.\n'
                        f'<b>{await get_username_msg(msg)}</b>, отправь срок выполнения задачи в формате "<i>01.01.2023</i>". '
                        f'Для отмены добавления задачи отправь /cancel')
            )
            logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND error past date')
            return
        await TaskStates.NEW_TASK_USER.set()
        await state.update_data(date_end=date_end)
        kb_new_task_user = await create_kb_new_task_user(msg.chat.id)
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, выберите кому назначена задача '
                                            f'<b><u>{task_data["title"]}</u></b>', reply_markup=kb_new_task_user)
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND date')


@dp.callback_query_handler(cb_new_task_user.filter(), state=TaskStates.NEW_TASK_USER)
@logger.catch
async def new_task_user(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    task_data = await state.get_data()
    if call.from_user.id == task_data['user_id_create']:
        new_task = await add_new_task_cmd(call.message.chat.id, call.from_user.id, task_data, callback_data['user_id'])
        logger.success(f'USER "{call.from_user.id} - {await get_username_call(call)}" ADD task')
        await state.finish()
        await bot.send_message(new_task.chat_id, await create_mes_task_to_chat(new_task), reply_markup=kb_to_chat)
        await update_show_chat(new_task)
        await call.answer()
        await call.message.delete()


################
### Удаление ###
################
@dp.message_handler(commands='delete')
@logger.catch
async def delete_task_cmd(msg: types.Message):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.\nДля '
                                                 'удалния задачи в боте выберите чат, выберите задачу,  потом нажмите кнопку "Удалить задачу"')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH delete_task_cmd IN BOT')
    else:
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH delete_task_cmd')
        await registration(msg=msg)
        await TaskStates.DELETE_TASK.set()
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, отправь id задачи для удаления.\n '
                                            f'Для отмены удаления задачи отправь /cancel')


@dp.message_handler(state=TaskStates.DELETE_TASK)
@logger.catch
async def delete_task_by_id_cmd(msg: types.Message, state: FSMContext):
    user = await get_user(msg.from_user.id)
    task = await get_task(msg.text)
    if task and task.chat.chat_id == msg.chat.id:
        title = task.title
        await state.finish()
        if user.super_admin or task.user_id_create == msg.from_user.id or await check_admin_chat(task.chat_id, msg.from_user.id):
            await del_task_by_id(task.id)
            await msg.reply(f'Задача <b>{title}</b> удалена.')
            logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" DELETE TASK')
        else:
            await bot.send_message(
                msg.chat.id,
                emojize(f':warning:Внимание!!!:warning:\n<b>{await get_username_msg(msg)}</b>, вы не можете удалить '
                        f'эту задачу.\n Вы должны быть автором задачи или модератором данного чата'))
            logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" DELETE TASK no privilege')
    else:
        await bot.send_message(msg.chat.id, emojize(f':warning:Внимание!!!:warning:\nЗадачи с таким id не существует.\n'
                f'<b>{await get_username_msg(msg)}</b>, отправь id задачи для удаления.\n '
                                            f'Для отмены удаления задачи отправь /cancel'))
        logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" DELETE TASK no task')


##################
### Выполнено! ###
##################


@dp.message_handler(commands='done')
@logger.catch
async def done_task_cmd(msg: types.Message):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.\nВ боте, '
             'чтобы отметить задачу выполненной выберите чат, выберите задачу,  потом нажмите кнопку "Выполнено"')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH done_task_cmd IN BOT')
    else:
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH done_task_cmd')
        await registration(msg=msg)
        await TaskStates.DONE_TASK.set()
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, отправь id задачи, чтобы ометить '
                                            f'ее выполненной.\n Для отмены отправь /cancel')


@dp.message_handler(state=TaskStates.DONE_TASK)
@logger.catch
async def delete_task_by_id_cmd(msg: types.Message, state: FSMContext):
    user = await get_user(msg.from_user.id)
    task = await get_task(msg.text)
    if task and task.chat.chat_id == msg.chat.id:
        title = task.title
        await state.finish()
        if user.super_admin or task.user_id_create == msg.from_user.id or \
                await check_admin_chat(task.chat_id, msg.from_user.id) or msg.from_user.id == task.for_user[0].user_id:
            await edit_complete(task, True)
            await msg.reply(f'Задача <b>{title}</b> выполнена.')
            logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" DONE TASK')
        else:
            await bot.send_message(
                msg.chat.id,
                emojize(f':warning:Внимание!!!:warning:\n<b>{await get_username_msg(msg)}</b>, вы не можете отметить '
            f'выполненной эту задачу.\n Вы должны быть автором либо исполнителем задачи или модератором данного чата'))
            logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" DONE TASK no privilege')
    else:
        await bot.send_message(msg.chat.id, emojize(f':warning:Внимание!!!:warning:\nЗадачи с таким id не существует.\n'
                                            f'<b>{await get_username_msg(msg)}</b>, отправь id задачи, чтобы ометить '
                                            f'ее выполненной.\n Для отмены отправь /cancel'))
        logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" DONE TASK no task')