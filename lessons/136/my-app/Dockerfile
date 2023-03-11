FROM golang:1.19.3-buster AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY server.go ./

RUN go build -o /my-app

FROM gcr.io/distroless/base-debian11

COPY --from=build /my-app /my-app

ENTRYPOINT ["/my-app"]
