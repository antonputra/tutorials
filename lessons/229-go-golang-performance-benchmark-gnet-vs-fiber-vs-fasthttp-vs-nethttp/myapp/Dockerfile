FROM golang:1.23.3-bookworm AS build

ARG APP_NAME

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -a -ldflags="-s -w" -installsuffix cgo -o myapp cmd/${APP_NAME}/main.go cmd/${APP_NAME}/server.go

FROM scratch

COPY --from=build /app/myapp /myapp

ENTRYPOINT ["/myapp"]
