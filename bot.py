import asyncio
import datetime

from aiogram.utils import executor

from func.function import *
from task_list import *
from task_current import *
from task_chat_cmd import *
from admin import *


@dp.message_handler(commands=['start'])
@logger.catch
async def start(msg: types.Message):
    mes = emojize(msg.from_user.first_name + ', добро пожаловать в "TaskBot" \n:waving_hand:')
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_start)
    logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" COMMAND START')


@dp.message_handler(commands='calendar')
async def start(message):
    calendar, step = DetailedTelegramCalendar().build()

    await bot.send_message(message.chat.id,
                           f"Select {LSTEP[step]}",
                           reply_markup=calendar)


@dp.callback_query_handler(DetailedTelegramCalendar.func())
async def inline_kb_answer_callback_handler(query):
    result, key, step = DetailedTelegramCalendar(locale='ru').process(query.data)

    if not result and key:
        await bot.edit_message_text(f"Select {LSTEP[step]}",
                                    query.message.chat.id,
                                    query.message.message_id,
                                    reply_markup=key)
    elif result:
        await bot.edit_message_text(f"You selected {result}",
                                    query.message.chat.id,
                                    query.message.message_id)


@dp.message_handler(commands=['i_am_superadmin'])
@logger.catch
async def superadmin(msg: types.Message):
    session.query(User).filter(User.t_id == msg.from_user.id).update({'super_admin': True}, synchronize_session='fetch')
    session.commit()
    await msg.reply('Теперь вы суперадмин.')


# @dp.message_handler(text=emojize('Проекты'))
# @logger.catch
# async def push_project(msg: types.Message):
#     await bot.send_message(msg.from_user.id, 'Раздел "Проекты" находится в разаботке')


@dp.message_handler(commands=['task9'])
@logger.catch
async def send_notice_tasks_9(msg: types.Message):
    print(9)
    date_now = datetime.datetime.now(tz=tz)
    day, hour, min, sec = date_now.day, date_now.hour, date_now.minute, date_now.second
    if date_now.hour < 9:
        time_delay = datetime.timedelta(days=day, hours=9) - datetime.timedelta(days=day, hours=hour, minutes=min, seconds=sec)
    else:
        time_delay = datetime.timedelta(days=day + 1, hours=9) - datetime.timedelta(days=day, hours=hour, minutes=min, seconds=sec)
    await asyncio.sleep(time_delay.seconds)
    while True:
        tasks_day = await tasks_this_day()
        for task in tasks_day:
            if not task.completed:
                try:
                    await bot.send_message(
                        task.chat_id,
                        emojize(
                            f':green_circle::green_circle::green_circle:\n'
                            f'Сегодня крайний срок выполнения задачи <u><b>"{task.title}"</b></u> (id {task.id})\n'
                            f'Кому назначено: <b><i>{task.for_user[0].user.name}</i></b>'
                        )
                    )
                except MigrateToChat:
                    logger.warning(f'MIGRATE migrate_to_chat_id - {msg.migrate_to_chat_id}, migrate_from_chat_id - {msg.migrate_from_chat_id}')
        if datetime.datetime.now(tz=tz).weekday() not in [5, 6]:
            users = await get_all_users()
            for user in users:
                user_tasks = await get_task_for_user(user.t_id)
                list_task = []
                if len(user_tasks) > 0:
                    for tfu in user_tasks:
                        list_task.append([tfu.task.date_end, tfu.task.completed, tfu.task.title, tfu.task.chat.title, tfu.task.id, tfu.task.description])
                        list_task.sort()
                    mes = '<b><u>Список назначенных вам задач:</u></b>\n'
                    num = 1
                    for t in list_task:
                        if not t[1] and t[0].timestamp() >= (
                                datetime.datetime.now(tz=tz) - datetime.timedelta(days=1)).timestamp():
                            mes += f'\n<b>{num}.</b> <b>{t[2]}</b> (id {t[4]})\nв чате <b><i>"{t[3]}"</i></b>'
                            mes += emojize(f'\nдо <i>{t[0].strftime("%d.%m.%Y")}</i>\n:green_circle::green_circle::green_circle:')
                            mes += f'\n{t[5]}\n'
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
        await asyncio.sleep(86400)


@dp.message_handler(commands=['task16'])
@logger.catch
async def send_notice_tasks_16(msg: types.Message):
    print(16)
    date_now = datetime.datetime.now(tz=tz)
    day, hour, min, sec = date_now.day, date_now.hour, date_now.minute, date_now.second
    if date_now.hour < 16:
        time_delay = datetime.timedelta(days=day, hours=16) - datetime.timedelta(days=day, hours=hour, minutes=min, seconds=sec)
    else:
        time_delay = datetime.timedelta(days=day + 1, hours=16) - datetime.timedelta(days=day, hours=hour, minutes=min, seconds=sec)
    await asyncio.sleep(time_delay.seconds)
    while True:
        if datetime.datetime.now(tz=tz).weekday() not in [5, 6]:
            users = await get_all_users()
            for user in users:
                user_tasks = await get_task_for_user(user.t_id)
                list_task = []
                if len(user_tasks) > 0:
                    for tfu in user_tasks:
                        list_task.append([tfu.task.date_end, tfu.task.completed, tfu.task.title, tfu.task.chat.title, tfu.task.id, tfu.task.description])
                        list_task.sort()
                    mes = '<b><u>Список ваших невыполненных задач:</u></b>\n'
                    num = 1
                    for t in list_task:
                        if not t[1] and t[0].timestamp() <= (
                                datetime.datetime.now(tz=tz) + datetime.timedelta(days=1)).timestamp():
                            mes += f'\n<b>{num}.</b> <b>{t[2]}</b> (id {t[4]})\nв чате <b><i>"{t[3]}"</i></b>'
                            mes += emojize(f'\nдо <i>{t[0].strftime("%d.%m.%Y")}</i>\n:green_circle::green_circle::green_circle:')
                            mes += f'\n{t[5]}\n'
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
        await asyncio.sleep(86400)


@dp.message_handler(commands=['start_timer'])
@logger.catch
async def timer(msg: types.Message):
    logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" START TIMER')
    tasks = []
    for remind in session.query(TimeReminder).all():
        if remind.time_reminder > datetime.datetime.now().time():
            seconds = await get_time_delay(remind.time_reminder.hour, remind.time_reminder.minute)
            tasks.append(asyncio.create_task(create_reminder(seconds, remind.task)))
    if datetime.time(hour=8) > datetime.datetime.now().time():
        tasks.append(asyncio.create_task(send_unexecuted_tasks(await get_time_delay(8, 0))))
    await asyncio.gather(*tasks)
    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_since_midnight = (now - midnight).total_seconds()
    await asyncio.sleep(86400 - seconds_since_midnight)
    while True:
        if datetime.datetime.now(tz=tz).weekday() not in [5, 6]:
            tasks = []
            for remind in session.query(TimeReminder).all():
                if remind.time_reminder > datetime.datetime.now().time():
                    seconds = await get_time_delay(remind.time_reminder.hour, remind.time_reminder.minute)
                    tasks.append(asyncio.create_task(create_reminder(seconds, remind.task)))
            tasks.append(asyncio.create_task(send_unexecuted_tasks(await get_time_delay(8, 0))))
            await asyncio.gather(*tasks)
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_since_midnight = (now - midnight).total_seconds()
        await asyncio.sleep(86400 - seconds_since_midnight)


@dp.message_handler(commands=['t'])
@logger.catch
async def test(msg: types.Message):
    user_tasks = await get_task_for_user(msg.from_user.id)
    list_task = []
    if user_tasks:
        for tfu in user_tasks:
            list_task.append([tfu.task.date_end, tfu.task.completed, tfu.task.title, tfu.task.chat.title, tfu.task.id, tfu.task.description])
            list_task.sort()
        mes = '<b><u>Список назначенных вам задач:</u></b>\n'
        num = 1
        for t in list_task:
            if not t[1] and t[0].timestamp() >= (datetime.datetime.now(tz=tz)-datetime.timedelta(days=1)).timestamp():
                mes += f'\n<b>{num}.</b> <b>{t[2]}</b> (id {t[4]})\nв чате <b><i>"{t[3]}"</i></b>'
                mes += emojize(f'\nдо <i>{t[0].strftime("%d.%m.%Y")}</i>\n:green_circle::green_circle::green_circle:')
                mes += f'\n{t[5]}\n'
                num += 1

        await bot.send_message(msg.from_user.id, mes)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
