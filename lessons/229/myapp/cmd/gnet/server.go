package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"myapp/config"
	"myapp/device"
	"strconv"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/evanphx/wildcat"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/panjf2000/gnet/v2"
	"github.com/prometheus/client_golang/prometheus"
)

var contentLengthKey = []byte("Content-Length")

type httpServer struct {
	gnet.BuiltinEventEngine
	addr      string
	multicore bool
	eng       gnet.Engine
	cfg       *config.Config
	db        *pgxpool.Pool
	m         *mon.Metrics
}

type httpCodec struct {
	parser        *wildcat.HTTPParser
	contentLength int
	buf           []byte
	body          []byte
	db            *pgxpool.Pool
	m             *mon.Metrics
}

var CRLF = []byte("\r\n\r\n")

func (hc *httpCodec) parse(data []byte, c gnet.Conn) (int, error) {
	bodyOffset, err := hc.parser.Parse(data)
	if err != nil {
		return 0, err
	}

	if hc.parser.Post() {
		body, err := io.ReadAll(hc.parser.BodyReader(data[bodyOffset:], c))
		if err != nil {
			panic(err)
		}
		hc.body = body
	}

	contentLength := hc.getContentLength()
	if contentLength > -1 {
		return bodyOffset + contentLength, nil
	}

	if idx := bytes.Index(data, CRLF); idx != -1 {
		return idx + 4, nil
	}

	return 0, errors.New("invalid http request")
}

func (hc *httpCodec) getContentLength() int {
	if hc.contentLength != -1 {
		return hc.contentLength
	}

	val := hc.parser.FindHeader(contentLengthKey)
	if val != nil {
		i, err := strconv.ParseInt(string(val), 10, 0)
		if err == nil {
			hc.contentLength = int(i)
		}
	}

	return hc.contentLength
}

func (hc *httpCodec) resetParser() {
	hc.contentLength = -1
}

func (hc *httpCodec) reset() {
	hc.resetParser()
	hc.buf = hc.buf[:0]
}

func (hc *httpCodec) appendResponse() {
	switch string(hc.parser.Path) {
	case "/healthz":
		getHealth(hc)
	case "/api/devices":
		if hc.parser.Get() {
			getDevices(hc)
		} else {
			hc.saveDevice()
		}
	default:
		msg := "404 page not found"
		hc.buf = append(hc.buf, "HTTP/1.1 404 Not Found\r\nServer: gnet\r\nContent-Type: text/plain; charset=utf-8\r\nDate: "...)
		hc.buf = getTime(hc)
		hc.buf = append(hc.buf, "\r\nX-Content-Type-Options: nosniff"...)
		hc.buf = append(hc.buf, []byte(fmt.Sprintf("\r\nContent-Length: %d\r\n\r\n", len(msg)))...)
		hc.buf = append(hc.buf, []byte(msg)...)
	}
}

func getHealth(hc *httpCodec) {
	msg := "OK"
	hc.buf = append(hc.buf, "HTTP/1.1 200 OK\r\nServer: gnet\r\nContent-Type: text/plain; charset=utf-8\r\nDate: "...)
	hc.buf = getTime(hc)
	hc.buf = append(hc.buf, []byte(fmt.Sprintf("\r\nContent-Length: %d\r\n\r\n", len(msg)))...)
	hc.buf = append(hc.buf, []byte(msg)...)
}

func getDevices(hc *httpCodec) {
	devices := []device.Device{
		{Id: 0, Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"},
		{Id: 1, Mac: "44-39-34-5E-9C-F2", Firmware: "3.0.1"},
		{Id: 2, Mac: "2B-6E-79-C7-22-1B", Firmware: "1.8.9"},
		{Id: 3, Mac: "06-0A-79-47-18-E1", Firmware: "4.0.9"},
		{Id: 4, Mac: "68-32-8F-00-B6-F4", Firmware: "5.0.0"},
	}

	b, err := json.Marshal(devices)
	if err != nil {
		fmt.Println(err)
		return
	}
	hc.buf = append(hc.buf, "HTTP/1.1 200 OK\r\nServer: gnet\r\nContent-Type: application/json\r\nDate: "...)
	hc.buf = getTime(hc)
	hc.buf = append(hc.buf, []byte(fmt.Sprintf("\r\nContent-Length: %d\r\n\r\n", len(b)))...)
	hc.buf = append(hc.buf, []byte(b)...)
}

func (hc *httpCodec) saveDevice() {
	ctx, done := context.WithCancel(context.Background())
	defer done()

	d := new(device.Device)
	err := json.Unmarshal(hc.body, &d)
	if err != nil {
		hc.m.Errors.With(prometheus.Labels{"op": "decode", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to decode device")
		getError(hc, "failed to unmarshal")
		return
	}

	sql := `INSERT INTO "gnet_device" (mac, firmware) VALUES ($1, $2) RETURNING id`
	err = d.Save(ctx, hc.db, hc.m, sql)
	if err != nil {
		hc.m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to save device")
		getError(hc, "failed to save device")
		return
	}
	slog.Debug("device saved", "id", d.Id, "mac", d.Mac, "firmware", d.Firmware)

	hc.buf = append(hc.buf, "HTTP/1.1 201 Created\r\nServer: gnet\r\nContent-Type: application/json\r\nDate: "...)
	hc.buf = time.Now().AppendFormat(hc.buf, "Mon, 02 Jan 2006 15:04:05 GMT")

	b, err := json.Marshal(d)
	if err != nil {
		fmt.Println(err)
		return
	}

	hc.buf = append(hc.buf, []byte(fmt.Sprintf("\r\nContent-Length: %d\r\n\r\n", len(b)))...)
	hc.buf = append(hc.buf, []byte(b)...)
}

func (hs *httpServer) OnBoot(eng gnet.Engine) gnet.Action {
	hs.eng = eng
	slog.Info("the server has started", "multi-core", hs.multicore, "port", hs.addr)
	return gnet.None
}

func (hs *httpServer) OnOpen(c gnet.Conn) ([]byte, gnet.Action) {
	c.SetContext(&httpCodec{parser: wildcat.NewHTTPParser(), m: hs.m, db: hs.db})
	return nil, gnet.None
}

func (hs *httpServer) OnTraffic(c gnet.Conn) gnet.Action {
	hc := c.Context().(*httpCodec)
	buf, _ := c.Next(-1)

pipeline:
	nextOffset, err := hc.parse(buf, c)
	if err != nil {
		goto response
	}

	hc.resetParser()
	hc.appendResponse()
	buf = buf[nextOffset:]
	if len(buf) > 0 {
		goto pipeline
	}
response:
	c.Write(hc.buf)
	hc.reset()
	return gnet.None
}

func getTime(hc *httpCodec) []byte {
	return time.Now().AppendFormat(hc.buf, "Mon, 02 Jan 2006 15:04:05 GMT")
}

func getError(hc *httpCodec, msg string) {
	hc.buf = append(hc.buf, "HTTP/1.1 500 Internal Server Error\r\nServer: gnet\r\nContent-Type: text/plain; charset=utf-8\r\nDate: "...)
	hc.buf = getTime(hc)
	hc.buf = append(hc.buf, []byte(fmt.Sprintf("\r\nContent-Length: %d\r\n\r\n", len(msg)))...)
	hc.buf = append(hc.buf, []byte(msg)...)
}
