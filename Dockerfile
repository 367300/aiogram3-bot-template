FROM python:3.11-slim

WORKDIR /app

# Устанавливаем OpenVPN и необходимые пакеты
RUN apt-get update && apt-get install -y \
    openvpn \
    curl \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/data

COPY ./src ./src
COPY ./main.py ./main.py
COPY ./requirements.txt ./requirements.txt
COPY ./vpn_manager.py ./vpn_manager.py
COPY ./vpn_config ./vpn_config

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

RUN chmod -R 777 /app/data

CMD ["python3", "main.py"]