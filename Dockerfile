FROM python:3.8-slim-buster

RUN python3 -m pip install --upgrade pip

COPY requirements.txt /
RUN python3 -m pip install -r /requirements.txt

COPY src/ /app
WORKDIR /app

ENTRYPOINT ["python3"]

CMD ["main.py"]