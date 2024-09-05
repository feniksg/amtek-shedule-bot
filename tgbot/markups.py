from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .utils import get_available_dates

def get_menu_markup():
    builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text="Расписание (Выбор даты) 🗓️",
            callback_data="choose_date"
        ),
        InlineKeyboardButton(
            text="Выбор класса 👥",
            callback_data="choose_class"
        ),
        InlineKeyboardButton(
            text="Автоматическая отправка расписания 🧑‍🏫",
            callback_data="set_time",
        ),
        InlineKeyboardButton(
            text="[Вкл/Выкл] Уведомления 🔔",
            callback_data='toggle_notifications'
        )
    ]
    builder.add(*buttons)
    builder.adjust(1, repeat=True)
    return builder.as_markup()

def get_grade_markup():
    builder = InlineKeyboardBuilder()
    builder.add(*[InlineKeyboardButton(text=str(i), callback_data=f"set_grade_{i}") for i in range(5, 12)])
    builder.add(InlineKeyboardButton(text="Назад", callback_data='grade_back'))
    builder.adjust(3,2,2,1)
    return builder.as_markup()

def get_grade_by_cmd_markup():
    builder = InlineKeyboardBuilder()
    builder.add(*[InlineKeyboardButton(text=str(i), callback_data=f"set_grade_{i}") for i in range(5, 12)])
    builder.add(InlineKeyboardButton(text="Назад", callback_data='grade_back_by_cmd'))
    builder.adjust(3,2,2,1)
    return builder.as_markup()

def get_letter_markup():
    builder = InlineKeyboardBuilder()
    builder.add(*[InlineKeyboardButton(text=str(i), callback_data=f"set_letter_{i}") for i in ['А', 'Б', 'В', 'Г']])
    builder.add(InlineKeyboardButton(text="Назад", callback_data='letter_back'))
    builder.adjust(4,1)
    return builder.as_markup()

async def get_available_dates_markup():
    builder = InlineKeyboardBuilder()
    dates = await get_available_dates()
    if not dates:
        return 'no-data'
    builder.add(*[
        InlineKeyboardButton(
            text=f'{date[0]} ({date[1]})',
            callback_data=f"get_day_schedule_{date[0]}"
        ) for date in dates
    ])
    builder.adjust(1)
    return builder.as_markup()

def get_time_c_markup():
    builder = InlineKeyboardBuilder()
    builder.add(*[
        InlineKeyboardButton(
            text="Добавить время",
            callback_data="add_time_auto"
        ),
    ])
    builder.adjust(1)
    return builder.as_markup()

def get_time_cud_markup():
    builder = InlineKeyboardBuilder()
    builder.add(*[
        InlineKeyboardButton(
            text="Добавить время",
            callback_data="add_time_auto"
        ),
        InlineKeyboardButton(
            text="Изменить время",
            callback_data="edit_time_auto"
        ),
        InlineKeyboardButton(
            text="Удалить время",
            callback_data="del_time_auto"
        ),
    ])
    builder.adjust(1)
    return builder.as_markup()

def get_time_ud_markup():
    builder = InlineKeyboardBuilder()
    builder.add(*[
        InlineKeyboardButton(
            text="Изменить время",
            callback_data="edit_time_auto"
        ),
        InlineKeyboardButton(
            text="Удалить время",
            callback_data="del_time_auto"
        ),
    ])
    builder.adjust(1)
    return builder.as_markup()

def get_selecting_tomorrow_or_today():
    builder = InlineKeyboardBuilder()
    builder.add(*[
        InlineKeyboardButton(
            text="Текущий день",
            callback_data="selecting_today"
        ),
        InlineKeyboardButton(
            text="Следующий день",
            callback_data="selecting_tomorrow"
        )
    ])
    builder.adjust(1)
    return builder.as_markup()