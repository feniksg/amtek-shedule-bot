from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ContentType, InputMediaPhoto
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta

import settings
from . import messages, markups
from .stategroups import (
    ClassSelection,
    TimeSelection,
    MakeReport,
    Broadcast,
    MessageTo
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
    delete_time_by_index,
    get_stats,
    get_users_for_broadcast
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

@dp.message(Command("help"))
async def cmd_help(message:Message):
    await message.answer(
        text=messages.message_help,
        parse_mode="HTML",
    )

#region Тех-поддержка

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


    

#endregion

#region Автоматическая отправка командой

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
    await callback.message.delete()
    await callback.message.answer(
        text=messages.set_time,
    )
    await state.set_state(TimeSelection.selecting_time)

@dp.callback_query(F.data == "del_time_auto")
async def call_del_time_auto(callback: CallbackQuery):
    times = await get_times_by_user(callback.from_user.id)
    await callback.message.edit_text(
        text="Выберите какое время хотите удалить:",
        reply_markup=markups.get_times_to_delete(times)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("delete_time_by_index_"))
async def call_delete_time_by_index(callback:CallbackQuery):
    index_to_delete = int(callback.data.split("_")[-1])
    await delete_time_by_index(callback.from_user.id, index_to_delete)
    await callback.message.delete()
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
                text=f"Уставновлено время {message.text}. \nВыберите какое расписание должно приходить в это время - Текущий или Следующий день",
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
    await callback.message.delete()
    await callback.message.answer(
        text="Время установлено!",
    )
    await state.clear()

@dp.callback_query(F.data == "selecting_tomorrow")
async def call_selecting_tomorrow(callback:CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time = data.get("notification_time", None)
    if time:
        await write_auto_schedule({"value": time, "mode": "tomorrow"}, callback.from_user.id)
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(
        text="Время установлено!",
    )
    await state.clear()

#endregion

#region Расписание по дате

@dp.message(Command("choose_date"))
async def cmd_choose_date(message:Message):
    mk = await markups.get_available_dates_markup()
    if mk=="no-data":
        await message.answer(
            text="Сейчас нет доступного расписания"
        )
        return
    await message.answer(
        text="<b>Выберите дату</b>:",
        parse_mode="HTML",
        reply_markup=mk
    )

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
    date = callback.data.split("_")[-1]
    date_obj = datetime.strptime(date, "%d.%m.%Y").astimezone(tz=settings.TZ_MOSCOW)
    weekday = date_obj.weekday()
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
    if photo == "no-data":
        await callback.message.answer(
            text="Расписания пока нет 😓"
        )
    elif photo:
        await bot.send_photo(
            callback.from_user.id,
            photo=photo,
            caption=f"Расписание {date} ({weekday})"
        )
        await callback.answer()
    else:
        await callback.message.answer(
            text="У вас не выбран класс."
        )

#endregion
    
#region Расписание на сегодня \ завтра
@dp.message(Command("today"))
async def cmd_today(message:Message):
    photo = await get_today_schedule(message.from_user.id)
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
            photo=photo,
            caption=f"Расписание на сегодня. {date} ({weekday})"
        )
    else:
        await message.answer(
            text="У вас не выбран класс."
        )

@dp.message(Command("tomorrow"))
async def cmd_tomorrow(message:Message):
    photo = await get_tomorrow_schedule(message.from_user.id)
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
            photo=photo,
            caption=f"Расписание на завтра. {date} ({weekday})"
        )
    else:
        await message.answer(
            text="У вас не выбран класс."
        )

#endregion

#region Уведомления

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
    await callback.message.delete()
    await callback.message.answer(
        text="Класс сохранён!",
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

#region Админка

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if str(message.from_user.id) == settings.ADMIN:
        data = await get_stats()
        mess_1 = f"Всего пользователей: {data['count']}\nУведомления включены: {data['notification']} - {data['persent']}%"
        mess_2 = ""
        for cls, count in data['class_count'].items():
            mess_2+=f"{cls}: {count}\n"

        await message.answer(mess_1)
        await message.answer(mess_2)
    else:
        await message.answer("Но но но мистер фиш")
    return

@dp.message(Command("list"))
async def cmd_list(message: Message):
    if str(message.from_user.id) == settings.ADMIN:
        data = await get_stats()
        n = 50
        devided_lists = [data['users_list'][i:i+n] for i in range(0, len(data['users_list']), n)]
        
        for l in devided_lists:
            temp = ""
            for tpl in l:
                temp+=f"@{tpl[0]} - {tpl[1]}\n"
            await message.answer(temp)
    else:
        await message.answer("Но но но мистер фиш")
    return

@dp.message(Command("broadcast"))
async def cmd_broadcast(message:Message, state:FSMContext):
    if str(message.from_user.id) == settings.ADMIN:
        await message.answer("Введите сообщение или загрузите изображение (одно) или видед (одно) для рассылки, или введите /cancel для отмены.")
        await state.set_state(Broadcast.waiting_for_message)
    else:
        await message.answer("Ты знаешь много лишнего 👀")
        
@dp.message(Broadcast.waiting_for_message,Command("cancel"))
async def cancel_broadcast(message: Message, state:FSMContext):
    await state.clear()
    await message.answer("Рассылка отменена.")

@dp.message(Broadcast.waiting_for_message,)
async def process_broadcast(message:Message, state:FSMContext):
    users = await get_users_for_broadcast()
    if message.content_type == ContentType.TEXT:
        broadcast_message = message.text
        for user_id in users:
            try:
                await bot.send_message(chat_id=user_id, text=broadcast_message, parse_mode="HTML")
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    elif message.content_type == ContentType.PHOTO:
        photo = message.photo
        caption = message.caption or ""
        for user_id in users:
            try:
                await bot.send_photo(chat_id=user_id, photo=photo[-1].file_id, caption=caption)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    elif message.content_type == ContentType.VIDEO:
        video = message.video
        caption = message.caption or ""
        for user_id in users:
            try:
                await bot.send_video(chat_id=user_id, video=video.file_id, caption=caption)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await state.clear()
    await message.answer("Рассылка завершена.")
   
@dp.message(Command("message_to"))
async def cmd_message_to(message: Message, state:FSMContext):
    if str(message.from_user.id) == settings.ADMIN:
        await message.answer("Включил режим пересылки /cancel работает по базе")
        await state.set_state(MessageTo.waiting_for_message)
    else:
        await message.answer("Не надо так делать...")

@dp.message(MessageTo.waiting_for_message, Command("cancel"))
async def cancel_message_to(message:Message, state: FSMContext):
    await state.clear()
    await message.answer("Выключил режим пересылки")

@dp.message(MessageTo.waiting_for_message)
async def process_message(message:Message, state: FSMContext):
    if "&" in message.text:
        dest_id = message.text.split("&")[0]
        users = await get_users_for_broadcast()
        if dest_id in users:
            await bot.send_message(chat_id=dest_id, text=message.text.split("&")[1])
        else:
            await message.answer("Такого id нет")
    else:
        await message.answer("telegram_id&text_dlua_otpravki")