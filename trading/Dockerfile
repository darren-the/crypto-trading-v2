FROM python:3.9.13
ARG WORKDIR=/app
WORKDIR ${WORKDIR}
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
