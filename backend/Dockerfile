FROM python:3.12-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем остальной код
COPY . .

# Экспортируем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]