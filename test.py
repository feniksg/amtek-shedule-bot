from datetime import datetime, timedelta

def get_dates_this_week():
    # Получаем сегодняшнюю дату
    today = datetime.now().date()

    # Генерируем список дат на этой неделе
    week_dates = [(today + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(7)]
    
    return week_dates

print(get_dates_this_week())