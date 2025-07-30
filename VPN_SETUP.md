# 🔒 Настройка VPN/Прокси для OpenAI API

Этот документ описывает способы настройки VPN или прокси только для запросов к OpenAI API, чтобы не держать VPN постоянно включенным.

## 🎯 Варианты реализации

### 1. **Прокси-сервер (Рекомендуется)**

Самый простой и эффективный способ - использовать прокси-сервер только для OpenAI API.

#### Настройка в .env файле:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Прокси для OpenAI (опционально)
OPENAI_PROXY_URL=http://proxy-server:port
OPENAI_PROXY_USERNAME=username  # если требуется аутентификация
OPENAI_PROXY_PASSWORD=password  # если требуется аутентификация
```

#### Примеры прокси:

```env
# HTTP прокси
OPENAI_PROXY_URL=http://proxy.example.com:8080

# SOCKS5 прокси
OPENAI_PROXY_URL=socks5://proxy.example.com:1080

# С аутентификацией
OPENAI_PROXY_URL=http://proxy.example.com:8080
OPENAI_PROXY_USERNAME=user
OPENAI_PROXY_PASSWORD=pass
```

### 2. **Локальный прокси-сервер**

Можно настроить локальный прокси, который будет перенаправлять только запросы к OpenAI API через VPN.

#### Установка и настройка:

```bash
# Установка прокси-сервера (например, nginx)
sudo apt install nginx

# Настройка nginx как прокси для OpenAI
sudo nano /etc/nginx/sites-available/openai-proxy
```

#### Конфигурация nginx:

```nginx
server {
    listen 8080;
    
    location / {
        proxy_pass https://api.openai.com;
        proxy_set_header Host api.openai.com;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Активация:

```bash
sudo ln -s /etc/nginx/sites-available/openai-proxy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Использование в .env:

```env
OPENAI_PROXY_URL=http://localhost:8080
```

### 3. **Docker с VPN**

Можно запустить бота в Docker контейнере с VPN.

#### Dockerfile с VPN:

```dockerfile
FROM python:3.11-slim

# Установка VPN клиента (например, OpenVPN)
RUN apt-get update && apt-get install -y openvpn

# Копирование конфигурации VPN
COPY vpn-config.ovpn /etc/openvpn/

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копирование кода приложения
COPY . .

# Скрипт запуска с VPN
COPY start-with-vpn.sh /start-with-vpn.sh
RUN chmod +x /start-with-vpn.sh

CMD ["/start-with-vpn.sh"]
```

#### Скрипт запуска start-with-vpn.sh:

```bash
#!/bin/bash

# Запуск VPN в фоне
openvpn --config /etc/openvpn/vpn-config.ovpn --daemon

# Ожидание подключения VPN
sleep 10

# Запуск бота
python main.py
```

### 4. **Системный VPN с маршрутизацией**

Настроить VPN так, чтобы только трафик к OpenAI API шел через VPN.

#### Настройка маршрутизации:

```bash
# Добавить маршрут только для OpenAI API
sudo ip route add 52.84.0.0/15 dev tun0  # OpenAI API диапазон
```

### 5. **OpenVPN с конфигурационным файлом (Рекомендуется для вашего случая)**

Если у вас есть OpenVPN конфигурационный файл (например, от ProtonVPN), вы можете настроить автоматическое подключение VPN только для запросов к OpenAI API.

#### Настройка в .env файле:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# OpenVPN конфигурационный файл
OVPN_CONFIG_PATH=/path/to/your/nl-free-221.protonvpn.udp.ovpn
```

#### Пример для вашего случая:

```env
# Путь к вашему файлу конфигурации ProtonVPN
OVPN_CONFIG_PATH=/home/user/nl-free-221.protonvpn.udp.ovpn
```

#### Как это работает:

1. **Автоматический запуск VPN** - при каждом запросе к OpenAI API бот автоматически запускает VPN
2. **Автоматическая остановка** - после завершения запроса VPN остается активным для последующих запросов
3. **Корректное завершение** - при остановке бота VPN автоматически отключается
4. **Проверка статуса** - бот проверяет, активен ли VPN, и не запускает его повторно

#### Требования:

- Установленный OpenVPN: `sudo apt install openvpn`
- Права sudo для запуска OpenVPN
- Валидный конфигурационный файл .ovpn

#### Проверка работы:

При запуске бота вы увидите:
```
🔒 VPN менеджер инициализирован: /path/to/your/nl-free-221.protonvpn.udp.ovpn
```

При запросе к OpenAI:
```
🔒 Запуск VPN для OpenAI API...
✅ VPN успешно запущен
🌍 VPN IP: 185.xxx.xxx.xxx
```

В ответе бота будет указано:
```
🔒 Запрос выполнен через VPN
```

## 🔧 Технические детали

### Поддерживаемые типы прокси:

- **HTTP прокси** - `http://proxy:port`
- **HTTPS прокси** - `https://proxy:port`
- **SOCKS4** - `socks4://proxy:port`
- **SOCKS5** - `socks5://proxy:port`

### Проверка работы прокси:

```bash
# Тест подключения к OpenAI через прокси
curl -x http://proxy:port https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Логирование:

Бот автоматически выводит информацию о настройке прокси при запуске:

```
🔒 OpenAI клиент настроен с прокси: http://proxy:port
```

или

```
🌐 OpenAI клиент настроен без прокси
```

## 🚀 Быстрый старт

1. **Выберите способ** (рекомендуется прокси-сервер)
2. **Настройте прокси** согласно инструкции выше
3. **Добавьте переменные в .env**:
   ```env
   OPENAI_PROXY_URL=http://your-proxy:port
   ```
4. **Запустите бота**:
   ```bash
   python main.py
   ```

## ⚠️ Важные замечания

- **Безопасность**: Используйте только доверенные прокси-серверы
- **Производительность**: Прокси может замедлить запросы
- **Надежность**: Добавьте обработку ошибок подключения к прокси
- **Мониторинг**: Следите за доступностью прокси-сервера

## 🔍 Диагностика проблем

### Проверка подключения:

```bash
# Тест прокси
curl -x http://proxy:port https://httpbin.org/ip

# Тест OpenAI API
curl -x http://proxy:port https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Логи ошибок:

Если прокси не работает, в логах бота будет ошибка подключения к OpenAI API.

## 📚 Дополнительные ресурсы

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [HTTPX Proxy Support](https://www.python-httpx.org/advanced/#proxies)
- [Nginx Proxy Configuration](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) 