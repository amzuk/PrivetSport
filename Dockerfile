FROM python:3.8-slim

WORKDIR /opt/app

RUN python3 -m pip install pipenv

ENV PIPENV_VENV_IN_PROJECT=1

ADD . /opt/app

RUN pipenv sync 

ARG TG_API_KEY

CMD [".venv/bin/python", "bot_telegram.py"]
