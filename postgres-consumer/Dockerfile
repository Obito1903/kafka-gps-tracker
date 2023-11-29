FROM golang:1.21

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download && go mod verify

COPY main.go main.go
RUN go build -v -o ./postgres-consumer ./main.go

COPY config.yaml config.yaml

ENTRYPOINT ["./postgres-consumer"]
