from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta

import settings
from . import messages, markups
from .stategroups import (
    ClassSelection,
    TimeSelection,
    MakeReport
)

from .utils import (
    check_user,
    add_user,
    set_class,
    toggle_notifications,
    get_today_schedule,
    get_tomorrow_schedule,
    get_schedule_by_date,
    get_times_by_user,
    write_auto_schedule,
    delete_time_by_index
)

bot = Bot(settings.TOKEN)

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if not await check_user(message.from_user.id):
        await add_user(message)
    await message.answer(text=messages.message_hello)
    await cmd_menu(message)

@dp.message(Command("menu"))
async def cmd_menu(message:Message):
    await message.answer(
        text=messages.message_menu,
        parse_mode="HTML",
        reply_markup=markups.get_menu_markup()
    )

@dp.message(Command("report"))
async def cmd_report(message:Message, state: FSMContext):
    await message.answer(
        text="Напишите текст обращения одним сообщением. Чтобы отменить обращение используйте команду /cancel"
    )
    await state.set_state(MakeReport.writing_report)

@dp.message(MakeReport.writing_report, Command("cancel"))
async def cmd_cancel_writing_report(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Вы отменили обращение в техническую поддержку!"
    )

@dp.message(MakeReport.writing_report)
async def writing_report_at_state(message: Message, state: FSMContext):
    await state.clear()
    await bot.send_message(
        chat_id=settings.ADMIN,
        text=f'Обращение от пользователя @{message.from_user.username}. Id пользователя {message.from_user.id}\n Обращение: "{message.text}"'
    )

@dp.callback_query(F.data == "set_time")
async def call_set_time(callback: CallbackQuery):
    times = await get_times_by_user(callback.from_user.id)
    match len(times):
        case 0:
            my_text="В данный момент у вас не установлено время автоматической отправки."
            mk=markups.get_time_c_markup()
        case 1 | 2:
            my_text = ""
            for time in times:
                if time['mode'] == 'today':
                    str_mode = '(Расписание на текущий день)'
                else:
                    str_mode = '(Расписание на следующий день)'
                my_text+=f'{times.index(time)+1}. {time["value"]} {str_mode}\n'
            mk=markups.get_time_cud_markup()
        case 3: 
            my_text = ""
            for time in times:
                if time['mode'] == 'today':
                    str_mode = '(Расписание на текущий день)'
                else:
                    str_mode = '(Расписание на следующий день)'
                my_text+=f'{times.index(time)+1}. {time["value"]} {str_mode}\n'
            mk=markups.get_time_ud_markup()
        case _:
            ...
    await callback.message.answer(
        text=my_text,
        reply_markup=mk
    )
    await callback.answer()

@dp.message(Command("set_time"))
async def cmd_set_time(message: Message):
    times = await get_times_by_user(message.from_user.id)
    match len(times):
        case 0:
            my_text="В данный момент у вас не установлено время автоматической отправки."
            mk=markups.get_time_c_markup()
        case 1 | 2:
            my_text = ""
            for time in times:
                if time['mode'] == 'today':
                    str_mode = '(Расписание на текущий день)'
                else:
                    str_mode = '(Расписание на следующий день)'
                my_text+=f'{times.index(time)+1}. {time["value"]} {str_mode}\n'
            mk=markups.get_time_cud_markup()
        case 3: 
            my_text = ""
            for time in times:
                if time['mode'] == 'today':
                    str_mode = '(Расписание на текущий день)'
                else:
                    str_mode = '(Расписание на следующий день)'
                my_text+=f'{times.index(time)+1}. {time["value"]} {str_mode}\n'
            mk=markups.get_time_ud_markup()
        case _:
            ...
    await message.answer(
        text=my_text,
        reply_markup=mk
    )


@dp.callback_query(F.data == "add_time_auto")
async def call_add_time_auto(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=messages.set_time,
        reply_markup=None
    )
    await state.set_state(TimeSelection.selecting_time)

@dp.callback_query(F.data == "del_time_auto")
async def call_del_time_auto(callback: CallbackQuery):
    times = await get_times_by_user(callback.from_user.id)
    await callback.message.answer(
        text="Выберите какое время хотите удалить:",
        reply_markup=markups.get_times_to_delete(times)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("delete_time_by_index_"))
async def call_delete_time_by_index(callback:CallbackQuery):
    index_to_delete = int(callback.data.split("_")[-1])
    await delete_time_by_index(callback.from_user.id, index_to_delete)
    await callback.message.answer(
        text="Время удалено"
    )
    await callback.answer()


@dp.message(TimeSelection.selecting_time)
async def write_selecting_time(message: Message, state: FSMContext):
    if len(message.text) == 5 and ":" in message.text and message.text.split(":")[0].isdigit() and message.text.split(":")[1].isdigit():
        hours = int(message.text.split(":")[0])
        minutes = int(message.text.split(":")[1])
        if hours >= 0 and hours <= 23 and minutes >= 0 and minutes <=59:
            await state.update_data(notification_time=message.text)
            await state.set_state(TimeSelection.selecting_tomorrow_or_today)
            await message.answer(
                text=f"Уставновлено время {message.text}. \n Выберите какое расписание должно приходить в это время - Текущий или Следующий день",
                reply_markup=markups.get_selecting_tomorrow_or_today()
            )
        else:
            await message.answer(
            text="Введено некорректное время"
            )
            await state.set_state(TimeSelection.selecting_time)
    else:
        await message.answer(
            text="Введено некорректное время"
        )
        await state.set_state(TimeSelection.selecting_time)

@dp.callback_query(F.data == "selecting_today")
async def call_selecting_today(callback:CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time = data.get("notification_time", None)
    if time:
        await write_auto_schedule({"value": time, "mode": "today"}, callback.from_user.id)
    await callback.answer()
    await callback.message.edit_text(
        text="Время установлено!",
        reply_markup=None
    )
    await state.clear()

@dp.callback_query(F.data == "selecting_tomorrow")
async def call_selecting_tomorrow(callback:CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time = data.get("notification_time", None)
    if time:
        await write_auto_schedule({"value": time, "mode": "tomorrow"}, callback.from_user.id)
    await callback.answer()
    await callback.message.edit_text(
        text="Время установлено!",
        reply_markup=None
    )
    await state.clear()



#region Расписание по дате

@dp.callback_query(F.data == "choose_date")
async def call_choose_date(callback: CallbackQuery):
    mk = await markups.get_available_dates_markup()
    if mk=="no-data":
        await callback.message.edit_text(
            text="Сейчас нет доступного расписания"
        )
        return
    await callback.message.edit_text(
        text="<b>Выберите дату</b>:",
        parse_mode="HTML",
        reply_markup=mk
    )

@dp.callback_query(F.data.startswith("get_day_schedule_"))
async def call_get_day_schedule(callback: CallbackQuery):
    photo = await get_schedule_by_date(date=callback.data.split("_")[-1], user_id=callback.from_user.id)
    if photo == "no-data":
        await callback.message.answer(
            text="Расписания пока нет 😓"
        )
    elif photo:
        await bot.send_photo(
            callback.from_user.id,
            photo=photo
        )
    else:
        await callback.message.answer(
            text="У вас не выбран класс."
        )

#endregion
    
#region Расписание на сегодня \ завтра
@dp.message(Command("today"))
async def cmd_today(message:Message):
    photo = await get_today_schedule(message.from_user.id)
    if photo == "sunday":
        await message.answer(
            text="Сегодня воскресенье, отдохни 😉"
        )
    elif photo == "no-data":
        await message.answer(
            text="Расписания пока нет 😓"
        )
    elif photo:
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=photo
        )
    else:
        await message.answer(
            text="У вас не выбран класс."
        )

@dp.message(Command("tomorrow"))
async def cmd_tomorrow(message:Message):
    photo = await get_tomorrow_schedule(message.from_user.id)
    if photo == "sunday":
        await message.answer(
            text="Завтра воскресенье, отдохни 😉"
        )
    elif photo == "no-data":
        await message.answer(
            text="Расписания пока нет 😓"
        )
    elif photo:
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=photo
        )
    else:
        await message.answer(
            text="У вас не выбран класс."
        )

#endregion

#region Автоматическая отправка расписания

@dp.callback_query(F.data == "toggle_notifications")
async def call_toggle_notifications(callback: CallbackQuery):
    result = await toggle_notifications(callback.from_user.id)
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=f"Уведомления {'включены 🔔' if result else 'выключены 🔕'}"
    )
    await callback.answer()

@dp.message(Command("toggle_notifications"))
async def cmd_toggle_notifications(message: Message):
    result = await toggle_notifications(message.from_user.id)
    await message.answer(
        text=f"Уведомления {'включены 🔔' if result else 'выключены 🔕'}"
    )
    

#endregion

#region Выбор класса

@dp.message(Command("choose_class"))
async def cmd_choose_class(message:Message, state: FSMContext):
    await message.answer(
        text=messages.message_choose_grade,
        parse_mode="HTML",
        reply_markup=markups.get_grade_by_cmd_markup()
    )
    await state.set_state(ClassSelection.selecting_grade)

@dp.callback_query(F.data == "grade_back_by_cmd")
async def call_back_by_cmd(callback: CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    except Exception as e:
        settings.logger.error(e)
    await state.clear()

@dp.callback_query(F.data == "choose_class")
async def call_choose_class(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=messages.message_choose_grade,
        parse_mode="HTML",
        reply_markup=markups.get_grade_markup()
    )
    await state.set_state(ClassSelection.selecting_grade)
    
@dp.callback_query(F.data.startswith('set_grade'))
async def call_set_grade(callback: CallbackQuery, state: FSMContext):
    await state.update_data(grade=callback.data.split("_")[-1])
    await callback.message.edit_text(
        text=messages.message_choose_letter,
        parse_mode="HTML",
        reply_markup=markups.get_letter_markup()
    )
    await state.set_state(ClassSelection.selecting_letter)

@dp.callback_query(F.data.startswith('set_letter'))
async def call_set_letter(callback: CallbackQuery, state: FSMContext):
    await state.update_data(letter=callback.data.split("_")[-1])
    await callback.message.edit_text(
        text="Класс сохранён!",
        reply_markup=None
    )
    data = await state.get_data()
    await set_class(callback.from_user.id, f"{data['grade']}{data['letter']}")
    await state.clear()
    
@dp.callback_query(F.data == "grade_back")
async def call_back_grade(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=messages.message_menu,
        parse_mode="HTML",
        reply_markup=markups.get_menu_markup()
    )
    await state.clear()

@dp.callback_query(F.data == "letter_back")
async def call_back_letter(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=messages.message_choose_grade,
        parse_mode="HTML",
        reply_markup=markups.get_grade_markup()
    )
    await state.set_state(ClassSelection.selecting_grade)

#endregion 


async def send_timetable(user_id, mode):
    if mode == "today":
        photo = await get_today_schedule(user_id)
        date = datetime.now()
        weekday = date.weekday()
        date = date.strftime("%d.%m.%Y")
        match weekday:
            case 0:
                weekday = "Понедельник"
            case 1:
                weekday = "Вторник"
            case 2:
                weekday = "Среда"
            case 3:
                weekday = "Четверг"
            case 4:
                weekday = "Пятница"
            case 5:
                weekday = "Суббота"
            case 6:
                weekday = "Воскресенье"
        if photo:
            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=f"Расписание на сегодня. {date} ({weekday})"
            )
        return
    elif mode == "tomorrow":
        photo = await get_tomorrow_schedule(user_id)
        date = datetime.now() + timedelta(days=1)
        weekday = date.weekday()
        date = date.strftime("%d.%m.%Y")
        match weekday:
            case 0:
                weekday = "Понедельник"
            case 1:
                weekday = "Вторник"
            case 2:
                weekday = "Среда"
            case 3:
                weekday = "Четверг"
            case 4:
                weekday = "Пятница"
            case 5:
                weekday = "Суббота"
            case 6:
                weekday = "Воскресенье"
        if photo:
            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=f"Расписание на завтра. {date} ({weekday})"
            )
    await bot.session.close()

async def send_notification(user_id, text):
    await bot.send_message(
        chat_id=user_id,
        text=text
    )
    await bot.session.close()