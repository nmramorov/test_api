FROM python:3.8-alpine

RUN apk add build-base
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install psycopg2

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]