from aiogram.utils import executor

from func.function import *
from task_list import *
from task_current import *
from admin import *


@dp.message_handler(commands=['start'])
@logger.catch
async def start(msg: types.Message):
    mes = emojize(msg.from_user.first_name + ', добро пожаловать в "TaskBot" \n:waving_hand:')
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_start)
    logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" COMMAND START')


@dp.message_handler(commands=['reg'])
@logger.catch
async def registration(msg: types.Message):
    logger.info(f'USER "{msg.from_user.id} - {await get_username_msg(msg)}" COMMAND REG')
    if msg.chat.id > 0:
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


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
