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
  -e POSTGRES_HOST=postgres \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DATABASE=postgres \
  micro-arch/postgres-consumer
```
