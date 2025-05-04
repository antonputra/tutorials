FROM golang:1.23.0-bookworm AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY . .

RUN CGO_ENABLED=0 GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o /myapp .

FROM scratch

COPY --from=build /myapp /myapp

ENTRYPOINT ["/myapp"]
