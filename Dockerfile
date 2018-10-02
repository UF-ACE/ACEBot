FROM python:3.7.0-alpine3.8

WORKDIR /usr/src/app

ADD . .

CMD ["python", "./bot.py"]