FROM python:3.11-slim

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY app.py ./app.py
COPY clean_app/ ./clean_app/
COPY config.json ./config.json
COPY main.py ./main.py
COPY assets/ ./assets/
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT 8080


CMD exec gunicorn --bind 0.0.0.0:$PORT --log-level info --workers 1 --threads 8 --timeout 0 main:server
