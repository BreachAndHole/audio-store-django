FROM python:3.10.0-alpine3.15

COPY requirements.txt /app/requirements.txt

RUN set -ex \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app
COPY . .

EXPOSE 8000

CMD ["python3", "cables_shop/manage.py", "runserver", "0.0.0.0:8000"]