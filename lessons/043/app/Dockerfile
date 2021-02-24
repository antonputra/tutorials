FROM golang:1.15.6-alpine3.12

WORKDIR /app

COPY go.mod .
COPY go.sum .

RUN go mod download

COPY main.go main.go

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o main main.go

ENTRYPOINT ["/app/main"]
