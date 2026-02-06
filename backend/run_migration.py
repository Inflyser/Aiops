#!/usr/bin/env python
import os
import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    # Настройка пути к alembic.ini
    alembic_cfg = Config("alembic.ini")
    
    # Установка URL базы данных из переменных окружения
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    # Выполнение миграций
    print("Running migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()


