import asyncio
import datetime
import os

from button import *
from func.task_current_func import *
from func.task_list_func import *


@dp.message_handler(commands='cancel', state=[
    TaskStates.NEW_TASK_TITLE,
    TaskStates.NEW_TASK_DESC,
    TaskStates.NEW_TASK_DATE,
    TaskStates.NEW_TASK_TITLE_BOT,
    TaskStates.NEW_TASK_DESC_BOT,
    TaskStates.NEW_TASK_DATE_BOT,
    TaskStates.DELETE_TASK,
    TaskStates.DONE_TASK,
    TaskStates.TIME_TASK
])
@logger.catch
async def cancel_new_task(msg: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(msg.chat.id, 'Отмена!')
    logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" CANCEL')

        ####################
        ### Ссылка в бот ###
        ####################


@dp.message_handler(commands=['bot'])
@logger.catch
async def link_to_bot(msg: types.Message):
    await bot.send_message(
        msg.chat.id,
        'Сссылка для перехода в бот\nВ боте есть дополнительные возможности для работы с задачами, такие как '
        'редактирование, сортировка и другие.\n Данная ссылка удалится через 15 секунд',
        reply_markup=kb_to_chat
    )
    logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" COMMAND BOT send link')
    await asyncio.sleep(15)
    await bot.delete_message(msg.chat.id, msg.message_id)
    await bot.delete_message(msg.chat.id, msg.message_id + 1)


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
        if await check_user(msg.from_user.id, msg):
            mes = f'Пользователь "{await get_username_msg(msg)}" добален в "TaskBot".'
            await bot.send_message(msg.chat.id, mes)
            logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" REG')
        if await check_user_in_chat(msg.chat.id, msg.from_user.id):
            mes = f'Пользователь "{await get_username_msg(msg)}" зарегистрирован в чате "{msg.chat.title}" в "TaskBot".'
            await bot.send_message(msg.chat.id, mes)
            logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" REG TO CHAT "{msg.chat.title}"')


@dp.message_handler(commands=['reg_chat'])
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

    # mes = emojize(msg.from_user.first_name + ", добро пожаловать в бот \n:waving_hand:")
    # await bot.send_message(msg.from_user.id, mes)
    # logger.info(f'Push "/start" - user "{msg.from_user.id} - {msg.from_user.username}"')
    # # await check_chat_participant(-1001789257723)
    # # await check_chat(-1001789257723)
    # a = await bot.get_chat_member(-1001789257723, 5468555552)
    # print(a.status)


        ####################
        ### Новая задача ###
        ####################


@dp.message_handler(commands=['new'])
@logger.catch
async def new_task_cmd(msg: types.Message, state: FSMContext):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.\nДля '
                     'добавления новой задачи в боте сначала выберите чат, а потом нажмите кнопку "Добавить задачу"')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH new_task_cmd IN BOT')
    else:
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH new_task_cmd')
        # await registration(msg=msg)
        await TaskStates.NEW_TASK_TITLE.set()
        await state.update_data(user_id_create=msg.from_user.id, chat_id=msg.chat.id, msg_id_del=msg.message_id)
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, отправь описание задачи.\n '
                                            f'Для отмены добавления задачи отправь /cancel')


@dp.message_handler(state=TaskStates.NEW_TASK_TITLE)
@logger.catch
async def new_task_title(msg: types.Message, state: FSMContext):
    task_data = await state.get_data()
    if msg.from_user.id == task_data['user_id_create']:
        await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'])
        await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'] + 1)
        await TaskStates.NEW_TASK_DATE.set()
        await state.update_data(title=msg.text, msg_id_del=msg.message_id)
        await bot.send_message(
            msg.chat.id,
            f'<b>{await get_username_msg(msg)}</b>, отправь срок выполнения задачи в формате "<i>01.01.2023</i>". '
            f'Для отмены добавления задачи отправь /cancel')
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND title')


# todo remove description
# @dp.message_handler(state=TaskStates.NEW_TASK_DESC)
# @logger.catch
# async def new_task_desc(msg: types.Message, state: FSMContext):
#     task_data = await state.get_data()
#     if msg.from_user.id == task_data['user_id_create']:
#         await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'])
#         await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'] + 1)
#         await TaskStates.NEW_TASK_DATE.set()
#         await state.update_data(description=msg.text, msg_id_del=msg.message_id)
#         await bot.send_message(
#             msg.chat.id,
#             f'<b>{await get_username_msg(msg)}</b>, отправь срок выполнения задачи в формате "<i>01.01.2023</i>". '
#             f'Для отмены добавления задачи отправь /cancel'
#         )
#         logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND description')


@dp.message_handler(state=TaskStates.NEW_TASK_DATE)
@logger.catch
async def new_task_date(msg: types.Message, state: FSMContext):
    task_data = await state.get_data()
    if msg.from_user.id == task_data['user_id_create']:
        try:
            date_end = datetime.datetime.strptime(msg.text, '%d.%m.%Y')
        except ValueError:
            await state.update_data(msg_id_del=msg.message_id)
            await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'])
            await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'] + 1)
            await bot.send_message(
                msg.chat.id,
                emojize(f':warning:Внимание!!!:warning:\nНеправильный формат даты!\n'
                f'<b>{await get_username_msg(msg)}</b>, отправь срок выполнения задачи в формате "<i>01.01.2023</i>". '
                        f'Для отмены добавления задачи отправь /cancel')
            )
            logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND error format date')
            return
        if date_end.timestamp() < (datetime.datetime.now(tz=tz) - datetime.timedelta(days=1)).timestamp():
            await state.update_data(msg_id_del=msg.message_id)
            await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'])
            await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'] + 1)
            await bot.send_message(
                msg.chat.id,
                emojize(f':warning:Внимание!!!:warning:\nВыбранная дата уже прошла, выберите дату в будущем.\n'
                        f'<b>{await get_username_msg(msg)}</b>, отправь срок выполнения задачи в формате "<i>01.01.2023</i>". '
                        f'Для отмены добавления задачи отправь /cancel')
            )
            logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND error past date')
            return
        await TaskStates.NEW_TASK_USER.set()
        await state.update_data(date_end=date_end, msg_id_del=msg.message_id)
        await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'])
        await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'] + 1)
        kb_new_task_user = await create_kb_new_task_user(msg.chat.id)
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, выберите кому назначена задача '
                                            f'<b><u>{task_data["title"]}</u></b>', reply_markup=kb_new_task_user)
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" SEND date')


@dp.callback_query_handler(text='cancel', state=TaskStates.NEW_TASK_USER)
@logger.catch
async def task_cancel(call: types.CallbackQuery, state: FSMContext):
    task_data = await state.get_data()
    await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'])
    await state.finish()
    await call.message.edit_text('Отмена добавления задачи.')
    await call.answer()
    logger.info(f'USER "{call.from_user.id} - {await get_username_call(call)}" CANCEL btn')


@dp.callback_query_handler(cb_new_task_user.filter(), state=TaskStates.NEW_TASK_USER)
@logger.catch
async def new_task_user(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    task_data = await state.get_data()
    if call.from_user.id == task_data['user_id_create']:
        await bot.delete_message(task_data['chat_id'], task_data['msg_id_del'])
        new_task = await add_new_task_cmd(call.message.chat.id, call.from_user.id, task_data, callback_data['user_id'])
        logger.success(f'USER "{call.from_user.id} - {await get_username_call(call)}" ADD task')
        await state.finish()
        await bot.send_message(new_task.chat_id, await create_mes_task_to_chat(new_task))
        await bot.send_message(callback_data['user_id'], await create_mes_task_to_user(new_task))
        await update_show_chat(new_task)
        await call.answer()
        await call.message.delete()


################
### Удаление ###
################


@dp.message_handler(commands='delete')
@logger.catch
async def delete_task_cmd(msg: types.Message, state: FSMContext):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.\nДля '
                                                 'удалния задачи в боте выберите чат, выберите задачу,  потом нажмите кнопку "Удалить задачу"')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH delete_task_cmd IN BOT')
    else:
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH delete_task_cmd')
        # await registration(msg=msg)
        await TaskStates.DELETE_TASK.set()
        await state.update_data(msg_id_del=msg.message_id)
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, отправь id задачи для удаления.\n '
                                            f'Для отмены удаления задачи отправь /cancel')


@dp.message_handler(state=TaskStates.DELETE_TASK)
@logger.catch
async def delete_task_by_id_cmd(msg: types.Message, state: FSMContext):
    user = await get_user(msg.from_user.id)
    task = await get_task(msg.text)
    if task and task.chat.chat_id == msg.chat.id:
        title = task.title
        task_data = await state.get_data()
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'])
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'] + 1)
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
        task_data = await state.get_data()
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'])
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'] + 1)
        await state.update_data(msg_id_del=msg.message_id)
        await bot.send_message(msg.chat.id, emojize(f':warning:Внимание!!!:warning:\nЗадачи с таким id не существует.\n'
                f'<b>{await get_username_msg(msg)}</b>, отправь id задачи для удаления.\n '
                                            f'Для отмены удаления задачи отправь /cancel'))
        logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" DELETE TASK no task')


        ##################
        ### Выполнено! ###
        ##################


@dp.message_handler(commands='done')
@logger.catch
async def done_task_cmd(msg: types.Message, state: FSMContext):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.\nВ боте, '
             'чтобы отметить задачу выполненной выберите чат, выберите задачу,  потом нажмите кнопку "Выполнено"')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH done_task_cmd IN BOT')
    else:
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH done_task_cmd')
        # await registration(msg=msg)
        await TaskStates.DONE_TASK.set()
        await state.update_data(msg_id_del=msg.message_id)
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, отправь id задачи, чтобы отметить '
                                            f'ее выполненной.\n Для отмены отправь /cancel')


@dp.message_handler(state=TaskStates.DONE_TASK)
@logger.catch
async def delete_task_by_id_cmd(msg: types.Message, state: FSMContext):
    user = await get_user(msg.from_user.id)
    task = await get_task(msg.text)
    if task and task.chat.chat_id == msg.chat.id:
        title = task.title
        task_data = await state.get_data()
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'])
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'] + 1)
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
        task_data = await state.get_data()
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'])
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'] + 1)
        await state.update_data(msg_id_del=msg.message_id)
        await bot.send_message(msg.chat.id, emojize(f':warning:Внимание!!!:warning:\nЗадачи с таким id не существует.\n'
                                            f'<b>{await get_username_msg(msg)}</b>, отправь id задачи, чтобы ометить '
                                            f'ее выполненной.\n Для отмены отправь /cancel'))
        logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" DONE TASK no task')


        #############################
        ### Задачи текущей недели ###
        #############################


@dp.message_handler(commands=['week'])
@logger.catch
async def send_week_task(msg: types.Message):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.\nВ боте '
                                                 'просмотреть список задач за разные периоды можно выбрав чат ')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH week_tasks_cmd IN BOT')
    else:
        # await registration(msg=msg)
        chat = await get_chat(msg.chat.id)
        start_date, stop_date = await start_stop_date('week')
        tasks = session.query(Task).filter(Task.chat_id == chat.chat_id,
                                           Task.date_end >= start_date, Task.date_end < stop_date
                                           ).order_by(Task.date_end).all()
        await bot.send_message(msg.chat.id, f'<u>Задачи текущей недели чата <b>{chat.title}</b> '
                                            f'({await get_count_tasks(chat, "week")}):</u>')
        for t in tasks:
            compl = ':check_mark_button:' if t.completed else ':cross_mark:'
            await bot.send_message(
                msg.chat.id,
                emojize(
                    f'{compl} <b>{t.title}</b> ({t.id})\n'
                    f'<i>(срок - {t.date_end.strftime("%d.%m.%Y")})</i>'
                )
            )
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH week_tasks_cmd')


        ######################
        ### Выгрузка Excel ###
        ######################


@dp.message_handler(commands=['excel'])
@logger.catch
async def send_excel_all_tasks(msg: types.Message):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.\nВ боте '
        'выгрузить список задач за разные периоды нужно выбрать чат, выбрать период времени - неделя, месяц или все и нажать кнопку "Excel" ')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH send_excel_cmd IN BOT')
    else:
        await registration(msg=msg)
        list_column = ['id', 'Автор задачи', 'Кому назначено', 'Срок выполнения', 'Задача']
        list_width = [7, 20, 20, 20, 60]
        chat = await get_chat(msg.chat.id)
        start_date = 0
        wb = Workbook()
        while True:
            oldest_task = await get_oldest_task(chat, start_date)
            if not oldest_task:
                break
            start, stop = await start_stop_week(oldest_task.date_end)
            ws = wb.create_sheet(f'{start.strftime("%d.%m.%Y")} - '
                                 f'{(stop-datetime.timedelta(days=1)).strftime("%d.%m.%Y")}')

            for n, col in enumerate(['A', 'B', 'C', 'D', 'E']):
                ws[f'{col}1'] = list_column[n]
                ws.column_dimensions[col].width = list_width[n]
            row = ws.row_dimensions[1]
            row.font = Font(bold=True, name='Calibri', size=12)

            tasks_week = await get_week_tasks(chat, start, stop)
            for n, t in enumerate(tasks_week):
                ws[f'A{n + 2}'] = t.id
                ws[f'B{n + 2}'] = t.user_create.name
                ws[f'C{n + 2}'] = t.for_user[0].user.name
                ws[f'D{n + 2}'] = t.date_end.strftime("%d.%m.%Y") if t.date_end else ''
                ws[f'E{n + 2}'] = t.title
                # ws[f'F{n + 2}'] = t.description

                row = ws.row_dimensions[n + 2]
                if t.completed:
                    row.fill = PatternFill("solid", fgColor="E2FFEC")
                else:
                    row.fill = PatternFill("solid", fgColor="FFE2E2")
                bd = Side(style='thin', color="000000")
                row.border = Border(left=bd, top=bd, right=bd, bottom=bd)
            start_date = stop
        start, stop = await start_stop_date('week')
        try:
            wb.active = wb[f'{start.strftime("%d.%m.%Y")} - '
                       f'{(stop - datetime.timedelta(days=1)).strftime("%d.%m.%Y")}']
        except KeyError:
            pass
        file_name = f'{chat.title}_Задачи.xlsx'
        wb.save(file_name)
        await bot.send_document(msg.chat.id, open(file_name, 'rb'))
        os.remove(file_name)


@dp.message_handler(commands=['my_excel'])
@logger.catch
async def send_excel_all_tasks(msg: types.Message):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.\nВ боте '
        'выгрузить список личных задач нужно выбрать чат и нажать кнопку "my_excel" ')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH send_my_excel_cmd IN BOT')
    else:
        list_column = ['id', 'Автор задачи', 'Срок выполнения', 'Задача']
        list_width = [7, 20, 20, 60]
        user = await get_user(msg.from_user.id)
        list_tfu = []
        for i in await get_task_for_user(msg.from_user.id):
            list_tfu.append([i.task.chat.title, i.task.date_end, i.task.title, i.task_id, i.task.user_create.name, i.task.completed])
        list_tfu.sort()
        wb = Workbook()
        sheet = list_tfu[0][0]
        num = 2
        for k, i in enumerate(list_tfu):
            if i[1].timestamp() >= (datetime.datetime.now(tz=tz) - datetime.timedelta(days=1)).timestamp():
                if k == 0 or i[0] != sheet or num == 2:
                    sheet = i[0]
                    num = 2
                    ws = wb.create_sheet(sheet)
                    for n, col in enumerate(['A', 'B', 'C', 'D']):
                        ws[f'{col}1'] = list_column[n]
                        ws.column_dimensions[col].width = list_width[n]
                    row = ws.row_dimensions[1]
                    row.font = Font(bold=True, name='Calibri', size=12)
                ws[f'A{num}'] = i[3]
                ws[f'B{num}'] = i[4]
                ws[f'C{num}'] = i[1].strftime("%d.%m.%Y")
                ws[f'D{num}'] = i[2]
                # ws[f'E{num}'] = i[5]
                row = ws.row_dimensions[num]
                if i[6]:
                    row.fill = PatternFill("solid", fgColor="E2FFEC")
                else:
                    row.fill = PatternFill("solid", fgColor="FFE2E2")
                bd = Side(style='thin', color="000000")
                row.border = Border(left=bd, top=bd, right=bd, bottom=bd)
                num += 1
        file_name = f'{user.name}_Задачи.xlsx'
        wb.save(file_name)
        await bot.send_document(msg.from_user.id, open(file_name, 'rb'))
        os.remove(file_name)
        await bot.delete_message(msg.chat.id, msg.message_id)


        ##############################
        ### Обновление данных чата ###
        ##############################


@dp.message_handler(commands=['update'])
@logger.catch
async def update_chat_data(msg: types.Message):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.from_user.id, 'Данная команда предназначена только для группового чата.')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH update_data_chat IN BOT')
    else:
        if session.query(Chat).filter(Chat.chat_id == msg.chat.id).first():
            session.query(Chat).filter(Chat.chat_id == msg.chat.id).update({'title': msg.chat.title}, synchronize_session='fetch')
            session.commit()
            logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" UPDATE data_chat TITLE')
            await bot.send_message(msg.chat.id, f'Название чата обновлено на <b>{msg.chat.title}</b>')
        else:
            parts = session.query(Participant).filter(Participant.user_id == msg.from_user.id).all()
            kb_update_chat = InlineKeyboardMarkup()
            for i in parts:
                kb_update_chat.row(InlineKeyboardButton(text=i.chat.title, callback_data=cb_update_chat.new(
                    chat_id=i.chat_id)))
            await bot.send_message(
                msg.chat.id,
                'Изменился ID данного чата. Для обновления базы данных выберите чат в котором вы сейчас '
                'находитесь:',
                reply_markup=kb_update_chat
            )


@dp.callback_query_handler(cb_update_chat.filter())
@logger.catch
async def update_chat_data_db(call:types.CallbackQuery, callback_data: dict):
    session.query(Chat).filter(Chat.chat_id == callback_data['chat_id']).update(
        {'chat_id': call.message.chat.id},
        synchronize_session='fetch'
    )
    session.query(Participant).filter(Participant.chat_id == callback_data['chat_id']).update(
        {'chat_id': call.message.chat.id},
        synchronize_session='fetch'
    )
    session.query(Task).filter(Task.chat_id == callback_data['chat_id']).update(
        {'chat_id': call.message.chat.id},
        synchronize_session='fetch'
    )
    session.commit()
    await call.message.edit_text('Данные чата обновлены.')
    await call.answer()
    logger.success(f'USER "{call.from_user.id} - {await get_username_call(call)}" UPDATE data_chat CHAT_ID')


#####################
### Выход из чата ###
#####################


@dp.message_handler(commands=['exit'])
@logger.catch
async def exit_chat(msg: types.Message):
    if msg.chat.id != msg.from_user.id:
        await bot.send_message(msg.chat.id, 'Данная команда предназначена только для использования в боте.')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH exit_chat IN CHAT')
    else:
        parts = session.query(Participant).filter(Participant.user_id == msg.from_user.id).all()
        kb_exit_chat = InlineKeyboardMarkup()
        for i in parts:
            kb_exit_chat.row(InlineKeyboardButton(text=i.chat.title, callback_data=cb_exit_chat.new(chat_id=i.chat_id)))
        await bot.send_message(
            msg.from_user.id,
            'Выберите чат для удаления. Вы не будете отслеживать задачи данного чата.',
            reply_markup=kb_exit_chat
        )


@dp.callback_query_handler(cb_exit_chat.filter())
@logger.catch
async def update_exit_chat_db(call:types.CallbackQuery, callback_data: dict):
    chat = await get_chat(callback_data['chat_id'])
    session.query(Participant).filter(
        Participant.user_id == call.from_user.id,
        Participant.chat_id == callback_data['chat_id']).delete()
    session.commit()
    await call.message.edit_text(f'Вы больше не отслеживаете задачи чата <b>{chat.title}</b>')
    await call.answer()
    logger.success(f'USER "{call.from_user.id} - {await get_username_call(call)}" EXIT CHAT')


    ############################
    ### список пользователей ###
    ############################


@dp.message_handler(commands=['user_list'])
@logger.catch
async def user_list(msg: types.Message):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.chat.id, 'Данная команда предназначена только для использования в чате.')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH user list IN BOT')
    else:
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" LIST USER')
        chat = await get_chat(msg.chat.id)
        mes = '<b><u>Список пользователей, зарегистрированнных в боте:</u></b>\n'
        for n, part in enumerate(chat.participants):
            mes += f'\n{n+1}. {part.user.name}'
        await bot.send_message(msg.chat.id, mes)


    ##################
    ###  reminder  ###
    ##################


@dp.message_handler(commands=['time'])
@logger.catch
async def new_reminder(msg: types.Message, state: FSMContext):
    if msg.chat.id == msg.from_user.id:
        await bot.send_message(msg.chat.id, 'Данная команда предназначена только для использования в чате.')
        logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH time list IN BOT')
    else:
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH time')
        await TaskStates.TIME_TASK.set()
        await state.update_data(msg_id_del=msg.message_id)
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, отправь id задачи и время в '
            'формате\n"id чч-мм"\n(например "111 09-30"), чтобы добавить время напоминания.\n Для отмены отправь /cancel')


@dp.message_handler(state=TaskStates.TIME_TASK)
@logger.catch
async def add_new_reminder(msg: types.Message, state: FSMContext):
    list_id_time = msg.text.split(' ')      # todo проверки неверного формата
    task = await get_task(list_id_time[0])
    if task and task.chat.chat_id == msg.chat.id:
        title = task.title
        task_data = await state.get_data()
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'])
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'] + 1)
        await state.finish()
        await msg.reply(f'Для задачи <b>{title}</b> добавлено напоминание на <i>{list_id_time[1]}</i>.')
        logger.success(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" ADD REMINDER TASK')
        await add_time_reminder(task.id, list_id_time[1])
    else:
        task_data = await state.get_data()
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'])
        await bot.delete_message(msg.chat.id, task_data['msg_id_del'] + 1)
        await state.update_data(msg_id_del=msg.message_id)
        await bot.send_message(msg.chat.id, emojize(f':warning:Внимание!!!:warning:\nЗадачи с таким id не существует.\n'
                                                    f'<b>{await get_username_msg(msg)}</b>, отправь id задачи и время в '
            'формате "id чч-мм" (например "111 09-30"), чтобы добавить время напоминания.\n Для отмены отправь /cancel'))
        logger.error(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" ADD REMINDER no task')


    ###############################
    ###  удаление пользователя  ###
    ###############################


@dp.message_handler(commands=['delete_user'])
@logger.catch
async def choose_user_for_delete(msg: types.Message, state: FSMContext):
    user = await get_user(msg.from_user.id)
    if user.super_admin:
        if msg.chat.id == msg.from_user.id:
            await bot.send_message(msg.chat.id, 'Данная команда предназначена только для использования в чате.')
            logger.warning(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" PUSH delete user IN BOT')
            return
        await TaskStates.USER_DELETE.set()
        kb_user_delete = await create_kb_user_delete(msg.chat.id)
        await bot.send_message(msg.chat.id, f'<b>{await get_username_msg(msg)}</b>, выберите пользователя для удаления', reply_markup=kb_user_delete)
        logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" CHOOSE USER DELETE')


@dp.callback_query_handler(text='cancel', state=TaskStates.USER_DELETE)
@logger.catch
async def user_delete_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text('Отмена удаления пользователя.')
    await call.answer()
    logger.info(f'USER "{call.from_user.id} - {await get_username_call(call)}" CANCEL btn')


@dp.callback_query_handler(cb_user_delete.filter(), state=TaskStates.USER_DELETE)
@logger.catch
async def user_delete(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    user_id = callback_data['user_id']
    user = await get_user(user_id)
    user_name = user.name
    session.query(Participant).filter(Participant.user_id == user_id).delete()
    session.query(TaskForUser).filter(TaskForUser.user_id == user_id).delete()
    for t in session.query(Task).filter(Task.user_id_create == user_id).all():
        session.query(TimeReminder).filter(TimeReminder.task_id == t.id).delete()
        session.query(TaskForUser).filter(TaskForUser.task_id == t.id).delete()
    session.query(Task).filter(Task.user_id_create == user_id).delete()
    session.query(User).filter(User.t_id == user_id).delete()
    session.commit()
    logger.success(f'USER "{call.from_user.id} - {await get_username_call(call)}" USER DELETE')
    await state.finish()
    await bot.send_message(call.message.chat.id, f'Пользователь <b>{user_name}</b> удален.')
    await call.message.delete()