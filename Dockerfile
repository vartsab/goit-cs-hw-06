FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install pymongo

CMD ["python", "main.py"]
