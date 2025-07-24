FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p /app/data

COPY ./src ./src
COPY ./main.py ./main.py
COPY ./requarement.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

RUN chmod -R 777 /app/data

CMD ["python3", "main.py"]