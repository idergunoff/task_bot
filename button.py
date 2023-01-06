from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from emoji import emojize


# CallbackData

cb_task = CallbackData("task", "task_id", 'page')    # выбор задачи
cb_chat_task = CallbackData('chat_task', 'chat_id')     # выбор чата для задач
cb_new_task = CallbackData('new_task', 'chat_id')   # id чата для новой задачи
cb_back_task = CallbackData('back_task', 'chat_id', 'page')     # id чата и номер страницы для выхода из просмотра задачи
cb_show_desc = CallbackData('show_desc', 'task_id', 'page')     # id задачи для показа описания
cb_not_show_desc = CallbackData('not_show_desc', 'task_id', 'page')     # id задачи для сворачивания описания
cb_show_comment = CallbackData('show_comment', 'task_id')     # id задачи для показа комментариев
cb_del_task = CallbackData('del_task', 'task_id')    # id задачи для удаления
cb_excel_tasks = CallbackData('excel_task', 'chat_id')  # id чата для выгрузки в Excel
cb_week_tasks = CallbackData('week_task', 'chat_id')  # id чата для списка задач за неделю
cb_month_tasks = CallbackData('month_task', 'chat_id')  # id чата для списка задач за месяц
cb_all_tasks = CallbackData('all_task', 'chat_id')  # id чата для полного списка задач
cb_edit_task = CallbackData('edit_task', 'task_id')  # id задачи для редактирования
cb_type_edit_task = CallbackData('type_edit_task', 'task_id', 'type_edit', 'page')  # id задачи и тип редактирования
cb_add_user_task = CallbackData('add_user_task', 'task_id', 'user_id', 'page')  # id задачи и id пользователя для добавления исполнителя
cb_new_task_user = CallbackData('new_task_user', 'user_id') # id пользователя исполнителя новой задачи для cmd
cb_page_list_task = CallbackData('page_list_task', 'chat_id', 'page') # номер страницы для списка задач

cb_admins = CallbackData('admins', 'chat_id') # id чата для меню админов
cb_add_admin = CallbackData('add_admin', 'chat_id') # id чата для добавления администратора
cb_del_admin = CallbackData('del_admin', 'chat_id') # id чата для удаления администратора
cb_add_user_admin = CallbackData('add_user_admin', 'chat_id', 'user_id') # id чата и юзера для добавления администратора
cb_del_user_admin = CallbackData('del_user_admin', 'chat_id', 'user_id') # id чата и юзера для удаления администратора
cb_back_admins = CallbackData('back_admins', 'chat_id') # id чата для возврата в меню админов
cb_back_task_admin = CallbackData('back_task_admin', 'chat_id') # id чата для выхода из меню админа


# KeyboardButton

btn_project = KeyboardButton(emojize('Проекты'))
btn_task = KeyboardButton(emojize('Задачи'))


# btn_send_phone = KeyboardButton(emojize(':mobile_phone:Отправить свой контакт'), request_contact=True)
# btn_back = KeyboardButton(emojize(':BACK_arrow:Назад'))


# InlineKeyboardButton

btn_back_chat_task = InlineKeyboardButton(emojize(':BACK_arrow:Назад'), callback_data='back_chat_task')
btn_to_bot = InlineKeyboardButton(emojize(':robot:Перейти в бот'), url='https://t.me/PlanTaskBot')

kb_to_chat = InlineKeyboardMarkup()
kb_to_chat.row(btn_to_bot)

# ReplyKeyboardMarkup

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_start.row(btn_project, btn_task)


class TaskStates(StatesGroup):
    NEW_TASK = State()
    EDIT_TITLE_TASK = State()
    EDIT_DESC_TASK = State()
    EDIT_DATE_TASK = State()

    NEW_TASK_TITLE = State()
    NEW_TASK_DESC = State()
    NEW_TASK_DATE = State()
    NEW_TASK_USER = State()

    DELETE_TASK = State()
    DONE_TASK = State()



