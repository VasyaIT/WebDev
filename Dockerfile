FROM python:3.10.6

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /webdev

RUN pip install --upgrade pip
COPY requirements.txt /webdev/
RUN pip install -r requirements.txt

COPY . /webdev/
RUN rm -rf /venv/