FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные зависимости включая postgresql-client
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Делаем скрипт исполняемым
RUN chmod +x /app/entrypoint.sh

# Экспортируем порт
EXPOSE 8000

# Запускаем скрипт, который выполнит миграции и запустит приложение
ENTRYPOINT ["/app/entrypoint.sh"]
