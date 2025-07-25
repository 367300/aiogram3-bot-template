# aiogram3-bot-template

> **Внимание!** Это основная ветка проекта, предназначенная для классического серверного (self-hosted, Docker) запуска с использованием SQLite. 
> Для деплоя в Яндекс Облако с YDB и Cloud Functions используйте ветку [yandex_cloud](https://github.com/367300/aiogram3-bot-template/tree/yandex_cloud).

## О проекте

Это учебный шаблон Telegram-бота на aiogram 3, реализующий квиз (викторину) с сохранением результатов пользователей и выводом статистики. Проект предназначен для изучения архитектуры современных Telegram-ботов, работы с асинхронным кодом, базой данных и масштабируемой структуры кода.

**Возможности:**
- Квиз с 10 вопросами по Python
- Сохранение результатов прохождения квиза для каждого пользователя
- Вывод статистики игроков (последний результат)
- Удобное меню с кнопками
- Маскировка никнейма в статистике для приватности
- Современная архитектура с разделением на модули

## Быстрый старт (Docker)

1. **Создайте файл .env в корне проекта и добавьте ваш токен Telegram-бота:**
   ```
   API_TOKEN_TG=ваш_токен_бота
   ```

2. **Постройте и запустите контейнер:**
   ```
   docker compose up --build -d
   ```

3. **Бот автоматически создаст базу данных в папке `data/`. Все результаты сохраняются между перезапусками контейнера.**

4. **Остановить контейнер:**
   ```
   docker compose down
   ```

## Архитектура проекта

```
project_root/
│
├── src/
│   ├── config.py         # Конфигурация (токен, путь к БД)
│   ├── database.py       # Работа с базой данных (создание, чтение, запись)
│   ├── keyboards.py      # Генерация клавиатур (меню, инлайн)
│   ├── quiz_data.py      # Вопросы квиза
│   └── handlers/         # Обработчики команд и логики
│       ├── __init__.py
│       ├── start.py      # /start и главное меню
│       ├── quiz.py       # Квиз: вопросы, ответы, логика
│       └── stats.py      # Статистика
│
├── main.py               # Точка входа (запуск бота)
├── Dockerfile            # Docker-инструкция для сборки образа
├── docker-compose.yml    # Docker Compose для автоматического запуска
├── requarement.txt       # Зависимости Python
├── data/                 # Папка для хранения базы данных (quiz_bot.db)
└── .env                  # Ваши секреты (токен бота)
```

## Примечания
- Для работы необходим Python 3.11+ (если запускать не через Docker).
- Все данные пользователей хранятся только у вас локально в файле `data/quiz_bot.db`.
- Для расширения функционала добавляйте новые обработчики в папку `src/handlers/`.

---

**Проект создан для учебных целей и легко расширяется под любые задачи Telegram-бота!**
