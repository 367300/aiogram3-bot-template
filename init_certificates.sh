#!/bin/bash

# Скрипт для загрузки и добавления сертификатов
echo "Загружаем сертификаты..."

# Загружаем сертификаты и добавляем их в файл certifi
curl -k "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt" -w "\n" >> $(python -m certifi)

echo "Сертификаты успешно добавлены!"

# Запускаем основное приложение
exec python main.py 