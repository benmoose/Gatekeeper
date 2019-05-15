FROM python:3.7 AS builder
ENV PYTHONUNBUFFERED 1

WORKDIR /wheels

COPY requirements*.txt requirements/
RUN pip wheel -r ./requirements/requirements.test.txt

FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1

COPY --from=builder /wheels /wheels

RUN pip install -r /wheels/requirements/requirements.test.txt -f /wheels \
    && rm -rf /wheels \
    && rm -rf /root/.cache/pip/*

WORKDIR /usr/src/app
COPY . .

ENTRYPOINT [ "operations/django/entrypoint.sh" ]
