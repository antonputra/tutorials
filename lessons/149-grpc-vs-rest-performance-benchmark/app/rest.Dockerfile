FROM golang:1.19.5-buster AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY serializer serializer
COPY event event
COPY cmd/rest-server cmd/rest-server

RUN go build -o /myapp cmd/rest-server/main.go

FROM gcr.io/distroless/base-debian11

COPY --from=build /myapp /myapp

ENTRYPOINT ["/myapp"]
