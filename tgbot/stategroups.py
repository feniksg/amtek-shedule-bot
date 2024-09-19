from aiogram.fsm.state import StatesGroup, State


class ClassSelection(StatesGroup):
    selecting_grade = State()
    selecting_letter = State()

class TimeSelection(StatesGroup):
    selecting_time = State()
    selecting_tomorrow_or_today = State()

class MakeReport(StatesGroup):
    writing_report = State()

class Broadcast(StatesGroup):
    waiting_for_message = State()

class MessageTo(StatesGroup):
    waiting_for_message = State()