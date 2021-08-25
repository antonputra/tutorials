FROM golang:1.17.0-alpine3.14 AS build

WORKDIR /src

COPY ./go.mod ./

RUN go mod download

COPY main.go .

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -installsuffix 'static' -o /app .

FROM gcr.io/distroless/static

USER nonroot:nonroot

COPY --from=build --chown=nonroot:nonroot /app /app

ENTRYPOINT ["/app"]
