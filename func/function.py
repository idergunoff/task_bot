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
