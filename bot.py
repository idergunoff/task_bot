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


@dp.message_handler(text=emojize('Проекты'))
@logger.catch
async def push_project(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Раздел "Проекты" находится в разаботке')


@dp.message_handler(commands=['bot'])
@logger.catch
async def test(msg: types.Message):
    print(msg.chat.id, msg.from_user.id)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
