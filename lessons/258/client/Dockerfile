FROM golang:1.24.2-bookworm AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o client -a -ldflags="-s -w" -installsuffix cgo

FROM scratch

COPY --from=build /app/client /client

ENTRYPOINT ["/client"]