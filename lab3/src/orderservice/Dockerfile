FROM python:3.9.9-slim-buster
WORKDIR /code
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt update && apt -y install dnsutils procps