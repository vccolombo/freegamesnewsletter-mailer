FROM python:3.8-alpine

RUN python -m pip install --upgrade pip

COPY requirements.txt /

RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt && \
    python -m pip install -r /requirements.txt && \
    apk del .build-deps

COPY src/ /app
WORKDIR /app

ENTRYPOINT ["python"]

CMD ["main.py"]