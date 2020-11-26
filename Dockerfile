FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code
RUN pip install -r requirements.txt
ADD . /code
ADD ./tg_bot /code/tg_bot
WORKDIR /code/tg_bot
