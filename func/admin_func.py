from config import *
from button import *
from func.function import *


@logger.catch
async def create_mes_admins(chat):
    mes = f'Администраторы чата <b>{chat.title}</b>:'
    for i in session.query(Participant).filter(Participant.chat_id == chat.chat_id, Participant.admin == True).all():
        mes += f'\n{i.user.name}'
    return mes


async def create_kb_admins(chat):

