FROM python:3-alpine
ENV PYTHONBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN apk add gcc linux-headers musl-dev zlib-dev jpeg-dev freetype-dev
RUN pip install -r requirements.txt
COPY . /app/