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
cb_page_list_task = CallbackData('page_list_task', 'chat_id', 'page') # номер страницы для списка задач

# KeyboardButton

btn_project = KeyboardButton(emojize('Проекты'))
btn_task = KeyboardButton(emojize('Задачи'))


# btn_send_phone = KeyboardButton(emojize(':mobile_phone:Отправить свой контакт'), request_contact=True)
# btn_back = KeyboardButton(emojize(':BACK_arrow:Назад'))


# InlineKeyboardButton

btn_back_chat_task = InlineKeyboardButton(emojize(':BACK_arrow:Назад'), callback_data='back_chat_task')

# ReplyKeyboardMarkup

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_start.row(btn_project, btn_task)


class TaskStates(StatesGroup):
    NEW_TASK = State()
    EDIT_TITLE_TASK = State()
    EDIT_DESC_TASK = State()
    EDIT_DATE_TASK = State()
