FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 80

ENV FASTAPI_DEBUG=1
ENV DEBUG=1
ENV LOG_LEVEL=1


CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "80", "--reload"]
