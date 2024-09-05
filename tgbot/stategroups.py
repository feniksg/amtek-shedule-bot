from aiogram.fsm.state import StatesGroup, State


class ClassSelection(StatesGroup):
    selecting_grade = State()
    selecting_letter = State()

class TimeSelection(StatesGroup):
    selecting_time = State()
    selecting_tomorrow_or_today = State()

class MakeReport(StatesGroup):
    writing_report = State()