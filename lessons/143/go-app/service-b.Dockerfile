FROM golang:1.19.4-buster AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY cmd/service-b/main.go ./cmd/service-b/

RUN go build -o /myapp cmd/service-b/main.go

FROM gcr.io/distroless/base-debian11

COPY --from=build /myapp /myapp

ENTRYPOINT ["/myapp"]
