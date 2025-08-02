FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p /app/data

# Устанавливаем curl для загрузки сертификатов
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY ./src ./src
COPY ./main.py ./main.py
COPY ./requirements.txt ./requirements.txt
COPY ./init_certificates.sh ./init_certificates.sh

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

RUN chmod -R 777 /app/data
RUN chmod +x /app/init_certificates.sh

# Загружаем и добавляем сертификаты
RUN curl -k "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt" -w "\n" >> $(python -m certifi)

CMD ["./init_certificates.sh"]