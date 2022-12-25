FROM python:3.9.13

WORKDIR /app

COPY setup.py .

RUN pip install .
