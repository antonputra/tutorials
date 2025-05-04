FROM golang:1.19.5-buster AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY main.go .

RUN go build -o /go-app main.go

FROM gcr.io/distroless/base-debian11

COPY --from=build /go-app /go-app

ENTRYPOINT ["/go-app"]
