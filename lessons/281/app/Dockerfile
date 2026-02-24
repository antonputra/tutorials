FROM golang:1.26.0-trixie AS build

WORKDIR /app

COPY go.mod .
COPY go.sum .

RUN go mod download && go mod verify

COPY main.go .

RUN CGO_ENABLED=0 go build -o client main.go

FROM scratch

COPY --from=build /app/client /client
