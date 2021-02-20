FROM python:3.7 AS builder
ENV PYTHONUNBUFFERED 1

WORKDIR /wheels

COPY requirements.txt requirements
RUN pip wheel -r ./requirements/requirements.txt

FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE django_conf.settings

COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir -r \
    /wheels/requirements/requirements.test.txt -f /wheels

WORKDIR /usr/src/app
COPY . .

ENTRYPOINT [ "operations/django/entrypoint.sh" ]
