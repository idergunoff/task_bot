import datetime

from config import *


# from telethon import TelegramClient


@logger.catch
async def get_user(user_id):
    return session.query(User).filter(User.t_id == user_id).first()


@logger.catch
async def get_chat(chat_id):
    return session.query(Chat).filter(Chat.chat_id == chat_id).first()


@logger.catch
async def get_task(task_id):
    return session.query(Task).filter(Task.id == task_id).first()


@logger.catch
async def check_chat(chat_id, title):
    if not session.query(Chat).filter(Chat.chat_id == chat_id).first():
        new_chat = Chat(chat_id=chat_id, title=title)
        session.add(new_chat)
        session.commit()
        return True


@logger.catch
async def check_user(user_id, msg):
    if not session.query(User).filter(User.t_id == user_id).first():
        new_user = User(t_id=user_id, name=await get_username_msg(msg))
        session.add(new_user)
        session.commit()
        return True


@logger.catch
async def check_user_in_chat(chat_id, user_id):
    if not session.query(Participant).filter(Participant.chat_id == chat_id, Participant.user_id == user_id).first():
        new_part = Participant(chat_id=chat_id, user_id=user_id)
        session.add(new_part)
        session.commit()
        return True


@logger.catch
async def get_username_msg(msg):
    name_list = []
    if msg.from_user.first_name:
        name_list.append(msg.from_user.first_name)
    if msg.from_user.last_name:
        name_list.append(msg.from_user.last_name)
    return ' '.join(name_list)


@logger.catch
async def get_username_call(call):
    name_list = []
    if call.from_user.first_name:
        name_list.append(call.from_user.first_name)
    if call.from_user.last_name:
        name_list.append(call.from_user.last_name)
    return ' '.join(name_list)


@logger.catch
async def get_last_task(user_id):
    return session.query(Task).filter(Task.user_id_edit == user_id).order_by(desc(Task.date_edit)).first()


@logger.catch
async def check_admin_chat(chat_id, user_id):
    return \
    session.query(Participant.admin).filter(Participant.chat_id == chat_id, Participant.user_id == user_id).first()[0]


@logger.catch
async def tasks_this_day():
    date_now = datetime.datetime.now(tz=tz)
    year, month, day = date_now.year, date_now.month, date_now.day
    yesterday = datetime.datetime(year, month, day - 1)
    tomorrow = datetime.datetime(year, month, day + 1)
    tasks = session.query(Task).filter(Task.date_end > yesterday, Task.date_end < tomorrow).order_by(
        Task.date_end).all()
    return tasks


@logger.catch
async def get_all_users():
    return session.query(User).all()


@logger.catch
async def get_task_for_user(user_id):
    return session.query(TaskForUser).filter(TaskForUser.user_id == user_id).all()


# async def check_chat_participant(chat_id):
#     api_id = 13984868
#     api_hash = 'b05d658e24c98a5684a50c693eaac68f'
#     client = TelegramClient('session_name', api_id, api_hash)
#     async with client:
#         async for user in client.iter_participants(chat_id):
#             print(user.id)

@logger.catch
async def create_reminder(delay, task):
    await asyncio.sleep(delay)
    if not task.completed:
        for tfu in task.for_user:
            mes = emojize(f':green_circle:<b>{task.title}</b> ({task.id})\n<i>(чат - {task.chat.title})</i>\n<i>(срок - '
                          f'{task.date_end.strftime("%d.%m.%Y")})</i>')
            await bot.send_message(tfu.user_id, mes)


@logger.catch
async def send_unexecuted_tasks(time_delay):
    await asyncio.sleep(time_delay)
    users = await get_all_users()
    for user in users:
        user_tasks = await get_task_for_user(user.t_id)
        list_task = []
        if len(user_tasks) > 0:
            for tfu in user_tasks:
                list_task.append(
                    [tfu.task.date_end, tfu.task.completed, tfu.task.title, tfu.task.chat.title, tfu.task.id])
                list_task.sort()
            mes = '<b><u>Список невыполненных задач:</u></b>\n'
            num = 1
            for t in list_task:
                if not t[1] and t[0].timestamp() <= ( datetime.datetime.now(tz=tz) + datetime.timedelta(days=1)).timestamp():
                    mes += emojize(f'\n<b>{num}.</b>\n:green_circle:<b>{t[2]}</b> ({t[4]})\n<i>(чат - {t[3]})</i>')
                    mes += f'\n<i>(срок - {t[0].strftime("%d.%m.%Y")})</i>'
                    num += 1
            if num > 1:
                try:
                    await bot.send_message(user.t_id, mes)
                except CantInitiateConversation:
                    mes = f'Бот не может отправить пользователю <b>{user.name}</b> сообщение. Пользователю ' \
                          f'<b>{user.name}</b> необходимо перейти в бот (/bot) и нажать старт.'
                    await bot.send_message(user_tasks[0].task.chat.chat_id, mes)
                    logger.error(f'USER "{user.t_id} - {user.name}" NOT START')
                except BotBlocked:
                    mes = f'Пользователь <b>{user.name}</b> заблокировал бот, поэтому бот не может отправить ' \
                          f'ему сообщение. Если пользователь больше не планирует пользоваться данным ботом, ' \
                          f'необходимо удалить назначенные ему задачи, чтобы не получать это сообщение.'
                    await bot.send_message(user_tasks[-1].task.chat.chat_id, mes)
                    logger.error(f'USER "{user.t_id} - {user.name}" BOT BLOCKED')


@logger.catch
async def get_time_delay(hour, minute):
    now = datetime.datetime.now()
    target_time = datetime.datetime(now.year, now.month, now.day, hour, minute, 0)
    delta = target_time - now
    return delta.total_seconds()