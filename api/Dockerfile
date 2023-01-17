FROM python:3.9.13
ARG WORKDIR=/app
WORKDIR ${WORKDIR}
COPY . .
RUN pip install -r requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS=${WORKDIR}/service_account_key.json
CMD python app.py
