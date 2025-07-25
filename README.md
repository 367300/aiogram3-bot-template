# aiogram3-bot-template (ветка yandex_cloud)

## О проекте

**Эта ветка предназначена для деплоя Telegram-бота на aiogram 3 в Яндекс Облако с использованием бессерверных вычислений (Yandex Cloud Functions) и облачной СУБД YDB.**

### Основные изменения по сравнению с основной веткой:
- Полный отказ от SQLite и Docker.
- Использование YDB (Yandex Database) для хранения состояния и результатов квиза.
- Архитектура serverless: точка входа реализована через webhook-функцию для Yandex Cloud Functions.
- Хэндлеры разделены по модулям и объединяются через общий роутер.
- Нет необходимости запускать event loop вручную — этим занимается облако.

## Возможности
- Квиз с вопросами по Python
- Сохранение результатов пользователей в YDB
- Вывод статистики игроков
- Маскировка никнейма в статистике
- Современная архитектура с разделением на модули

## Быстрый старт (Yandex Cloud)

1. **Создайте таблицы в YDB вручную (например, через YDB Console):**

   ```sql
   -- Таблица состояния пользователя (индекс вопроса и текущие очки)
   CREATE TABLE `quiz_state` (
       user_id Uint64,
       question_index Uint64,
       PRIMARY KEY (`user_id`)
   );

   -- Таблица результатов квиза
   CREATE TABLE `quiz_results` (
       user_id Uint64,
       username Utf8,
       correct_answers Uint64,
       PRIMARY KEY (`user_id`)
   );

   -- Таблица вопросов квиза
   CREATE TABLE `quiz_questions` (
       id Uint64,
       question Utf8,
       options Utf8,           -- варианты ответа через | (вертикальная черта)
       correct_option Uint64,
       PRIMARY KEY (id)
   );
   ```

2. **Пример заполнения таблицы вопросов:**

   ```sql
   UPSERT INTO quiz_questions (id, question, options, correct_option) VALUES
   (0, "Что такое Python?", "Язык программирования|Тип данных|Музыкальный инструмент|Змея на английском", 0);

   UPSERT INTO quiz_questions (id, question, options, correct_option) VALUES
   (1, "Какой тип данных используется для хранения целых чисел?", "int|float|str|natural", 0);
   ```

   > Варианты ответа перечисляются через символ | (вертикальная черта), индексация с нуля.

3. **Настройте переменные окружения для функции:**
   - `API_TOKEN_TG` — токен Telegram-бота
   - `YDB_ENDPOINT` — endpoint вашей YDB (например, `grpcs://ydb.serverless.yandexcloud.net:2135`)
   - `YDB_DATABASE` — путь к базе (например, `/ru-central1/b1g.../etn...`)

4. **Задеплойте проект как Yandex Cloud Function:**
   - В качестве точки входа используйте файл `tb_webhook.py` и функцию `webhook`.
   - Укажите необходимые переменные окружения.
   - Настройте webhook Telegram на URL вашей функции.

## Архитектура проекта

```
project_root/
│
├── src/
│   ├── config.py         # Конфигурация (токен, параметры YDB)
│   ├── database.py       # Работа с YDB (чтение, запись)
│   ├── keyboards.py      # Генерация клавиатур (меню, инлайн)
│   ├── quiz_data.py      # Вопросы квиза
│   └── handlers/         # Обработчики команд и логики
│       ├── __init__.py   # Объединяющий роутер
│       ├── start.py      # /start и главное меню
│       ├── quiz.py       # Квиз: вопросы, ответы, логика
│       └── stats.py      # Статистика
│
├── tb_webhook.py         # Точка входа для Yandex Cloud Functions (webhook)
├── requarement.txt       # Зависимости Python
└── .env                  # Ваши секреты (токен бота, параметры YDB)
```

## Примечания
- Для работы необходим Python 3.11+ (локально — для тестирования).
- Все данные пользователей хранятся в облачной базе YDB.
- Для расширения функционала добавляйте новые обработчики в папку `src/handlers/` и подключайте их в `src/handlers/__init__.py`.
- Локальный запуск через polling не поддерживается — только webhook/cloud functions.

---

**Проект адаптирован для учебных и продакшн-задач в Яндекс Облаке!**
