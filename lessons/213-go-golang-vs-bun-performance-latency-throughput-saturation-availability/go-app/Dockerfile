FROM golang:1.23.2-bookworm AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY . .

RUN go generate

RUN CGO_ENABLED=0 GOARCH=amd64 GOOS=linux GOAMD64=v2 go build -trimpath -tags osusergo,netgo -o server -a -ldflags="-s -w -buildid=" -gcflags="all=-m=0 -l=2 -dwarf=false" -installsuffix cgo

FROM scratch

COPY --from=build /app/server /server

ENTRYPOINT ["/server"]
