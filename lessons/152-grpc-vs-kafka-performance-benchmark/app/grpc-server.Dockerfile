# FROM golang:1.19.5-buster AS build
FROM golang:1.19.5 AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY proto proto
COPY cmd/grpc-server cmd/grpc-server

RUN go build -o /grpc-server cmd/grpc-server/main.go

FROM gcr.io/distroless/base-debian11

COPY --from=build /grpc-server /grpc-server

ENTRYPOINT ["/grpc-server"]