FROM python:3.7 AS builder
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements*.txt /requirements/
RUN pip install -r /requirements/requirements.test.txt

COPY . .
