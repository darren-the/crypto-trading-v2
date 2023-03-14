FROM python:3.9.13
ARG WORKDIR=/app
WORKDIR ${WORKDIR}
COPY . .
RUN pip install -r requirements.txt
CMD ["flask", "run", "--host=0.0.0.0", "--port=4000"]
