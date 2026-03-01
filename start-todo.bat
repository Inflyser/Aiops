@echo off
title To-do App Launcher
color 0A

echo ========================================
echo        🚀 TO-DO APP LAUNCHER
echo ========================================
echo.

:: Путь к проекту (поменяйте на свой!)
set PROJECT_PATH=C:\Users\%USERNAME%\Documents\GitHub\todo-app

:: Переходим в папку проекта
cd /d %PROJECT_PATH%

:: Проверяем Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo 📦 Docker не запущен. Запускаю...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Ожидаем 30 секунд...
    timeout /t 30 /nobreak
)

:: Запускаем приложение
echo.
echo 🐳 Запускаю контейнеры...
docker-compose up -d

:: Проверяем результат
if errorlevel 1 (
    echo.
    echo ❌ Ошибка при запуске!
    pause
    exit /b 1
)

:: Открываем браузер
echo.
echo 🌐 Открываю приложение...
timeout /t 5 /nobreak
start http://localhost:8080

:: Показываем статус
echo.
echo 📊 Текущий статус:
docker-compose ps

echo.
echo ========================================
echo ✅ Приложение успешно запущено!
echo 📍 Адрес: http://localhost:8080
echo ========================================
echo.
echo Нажмите любую клавишу для выхода...
pause >nul