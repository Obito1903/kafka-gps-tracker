# PostgreSQL Consumer

## Build

```bash
docker build -t micro-arch/postgres-consumer .
```

## Run

```bash
docker run -it --rm --name postgres-consumer micro-arch/postgres-consumer
```

With environment variables:

```bash
docker run -it --rm --name postgres-consumer \
  -e CONS_KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
  -e CONS_KAFKA_TOPIC=topic \
  -e CONS_POSTGRES_HOST=postgres \
  -e CONS_POSTGRES_PORT=5432 \
  -e CONS_POSTGRES_USER=user \
  -e CONS_POSTGRES_PASSWORD=password \
  -e CONS_POSTGRES_DATABASE=database \
  micro-arch/postgres-consumer
```

With config file:

```bash
docker run -it --rm --name postgres-consumer \
  -v $(pwd)/config.yaml:/config.yaml \
  micro-arch/postgres-consumer
```

## Configuration

| Environment Variable           | Config File Key           | Description             | Default        |
| ------------------------------ | ------------------------- | ----------------------- | -------------- |
| `CONS_KAFKA_BOOTSTRAP_SERVERS` | `kafka.bootstrap.servers` | Kafka bootstrap servers | localhost:9092 |
| `CONS_KAFKA_TOPIC`             | `kafka.topic`             | Kafka topic             | topic          |
| `CONS_KAFKA_GROUP`             | `kafka.group`             | Kafka consumer grou     | gps-consumer   |
| `CONS_POSTGRES_HOST`           | `postgres.host`           | PostgreSQL host         | localhost      |
| `CONS_POSTGRES_PORT`           | `postgres.port`           | PostgreSQL port         | 5432           |
| `CONS_POSTGRES_USER`           | `postgres.user`           | PostgreSQL user         | tracker        |
| `CONS_POSTGRES_PASSWORD`       | `postgres.password`       | PostgreSQL password     | tracker        |
| `CONS_POSTGRES_DATABASE`       | `postgres.database`       | PostgreSQL database     | tracker        |
| `CONS_POSTGRES_TABLE`          | `postgres.table`          | PostgreSQL table        | position       |
