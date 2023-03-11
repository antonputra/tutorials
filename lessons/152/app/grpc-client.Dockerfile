# FROM golang:1.19.5-buster AS build
FROM golang:1.19.5 AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY proto proto
COPY cmd/grpc-client cmd/grpc-client

RUN go build -o /grpc-client cmd/grpc-client/main.go

FROM gcr.io/distroless/base-debian11

COPY --from=build /grpc-client /grpc-client

ENTRYPOINT ["/grpc-client"]