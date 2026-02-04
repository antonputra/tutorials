FROM golang:1.25.6-alpine3.23 AS builder

WORKDIR /app

COPY go.mod ./

RUN go mod download

COPY . .

RUN go build -o server .

FROM alpine:3.23.3

WORKDIR /root/

COPY --from=builder /app/server .

CMD ["./server"]
