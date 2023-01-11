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


@dp.message_handler(commands=['bot'])
@logger.catch
async def test(msg: types.Message):
    print(msg.chat.id, msg.from_user.id)


@dp.message_handler(commands=['task'])
@logger.catch
async def send_notice_tasks(msg: types.Message):
    print(1)
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
                await bot.send_message(
                    task.chat_id,
                    emojize(
                        f':green_circle::green_circle::green_circle:\n'
                        f'Сегодня крайний срок выполнения задачи <u><b>"{task.title}"</b></u> (id {task.id})\n'
                        f'Кому назначено: <b><i>{task.for_user[0].user.name}</i></b>'
                    )
                )

        users = await get_all_users()
        for user in users:
            user_tasks = await get_task_for_user(user.t_id)
            mes = '<b><u>Список назначенных вам задач:</u></b>\n'
            num = 1
            for tfu in user_tasks:
                if not tfu.task.completed:
                    mes += f'\n{num}. <b>{tfu.task.title}</b> в чате {tfu.task.chat.title} до <i>{tfu.task.date_end.strftime("%d.%m.%Y")}</i>'
                    num += 1
            if num > 1:
                await bot.send_message(user.t_id, mes)

        await asyncio.sleep(86400)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
