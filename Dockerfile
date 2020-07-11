FROM python:3.8-slim-buster

RUN python -m pip install --upgrade pip

COPY requirements.txt /
RUN python -m pip install -r /requirements.txt

COPY src/ /app
WORKDIR /app

ENTRYPOINT ["python"]

CMD ["main.py"]