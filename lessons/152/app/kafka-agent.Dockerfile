# FROM golang:1.19.5-buster AS build
FROM golang:1.19.5 AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY proto proto
COPY cmd/kafka-agent cmd/kafka-agent

RUN go build -o /kafka-agent cmd/kafka-agent/main.go

FROM gcr.io/distroless/base-debian11

COPY --from=build /kafka-agent /kafka-agent

ENTRYPOINT ["/kafka-agent"]