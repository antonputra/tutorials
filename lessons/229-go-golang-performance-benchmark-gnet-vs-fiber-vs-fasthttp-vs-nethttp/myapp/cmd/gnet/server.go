package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"log/slog"
	"net/http"
	"strconv"
	"sync"
	"time"

	"myapp/config"
	"myapp/device"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/evanphx/wildcat"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/panjf2000/ants/v2"
	"github.com/panjf2000/gnet/v2"
	"github.com/panjf2000/gnet/v2/pkg/pool/goroutine"
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
	resp          bytes.Buffer
	db            *pgxpool.Pool
	m             *mon.Metrics
}

var (
	CRLF      = []byte("\r\n\r\n")
	lastChunk = []byte("0\r\n\r\n")
)

func (hc *httpCodec) parse(data []byte) (int, []byte, error) {
	bodyOffset, err := hc.parser.Parse(data)
	if err != nil {
		return 0, nil, err
	}

	contentLength := hc.getContentLength()
	if contentLength > -1 {
		bodyEnd := bodyOffset + contentLength
		var body []byte
		if len(data) >= bodyEnd {
			body = data[bodyOffset:bodyEnd]
		}
		return bodyEnd, body, nil
	}

	// Transfer-Encoding: chunked
	if idx := bytes.Index(data[bodyOffset:], lastChunk); idx != -1 {
		bodyEnd := idx + 5
		var body []byte
		if len(data) >= bodyEnd {
			req, err := http.ReadRequest(bufio.NewReader(bytes.NewReader(data[:bodyEnd])))
			if err != nil {
				return bodyEnd, nil, err
			}
			body, _ = io.ReadAll(req.Body)
		}
		return bodyEnd, body, nil
	}

	// Request without a body.
	if idx := bytes.Index(data, CRLF); idx != -1 {
		return idx + 4, nil, nil
	}

	return 0, nil, errors.New("invalid http request")
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
	hc.resp.Reset()
}

var (
	healthzPath = []byte("/healthz")
	devicesPath = []byte("/api/devices")
)

func writeResponse(c gnet.Conn, body []byte) {
	hc := c.Context().(*httpCodec)

	switch hc.parser.Path {
	case healthzPath:
		appendResponse(&hc.resp, "HTTP/1.1 200 OK", "OK")
	case devicesPath:
		if hc.parser.Get() {
			getDevices(hc)
		} else {
			saveDevice(c, hc, body)
		}
	default:
		appendResponse(&hc.resp, "HTTP/1.1 404 Not Found", "404 page not found", "X-Content-Type-Options: nosniff")
	}
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
		appendError(&hc.resp, "failed to marshal devices")
		return
	}
	appendResponse(&hc.resp, "HTTP/1.1 200 OK", b, "Content-Type: application/json")
}

var (
	bufPool    = sync.Pool{New: func() any { return &bytes.Buffer{} }}
	workerPool = goroutine.Default()
)

func saveDevice(c gnet.Conn, hc *httpCodec, body []byte) {
	ctx, done := context.WithCancel(context.Background())
	defer done()

	d := new(device.Device)
	err := json.Unmarshal(body, &d)
	if err != nil {
		hc.m.Errors.With(prometheus.Labels{"op": "decode", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to decode device")
		appendError(&hc.resp, "failed to unmarshal")
		return
	}

	err = workerPool.Submit(func() {
		buf := bufPool.Get().(*bytes.Buffer)

		sql := `INSERT INTO "gnet_device" (mac, firmware) VALUES ($1, $2) RETURNING id`
		err := d.Save(ctx, hc.db, hc.m, sql)
		if err != nil {
			hc.m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
			util.Warn(err, "failed to save device")
			appendError(buf, "failed to save device")
			c.AsyncWrite(buf.Bytes(), func(c gnet.Conn, err error) error {
				buf.Reset()
				bufPool.Put(buf)
				return nil
			})
			return
		}
		slog.Debug("device saved", "id", d.Id, "mac", d.Mac, "firmware", d.Firmware)

		b, err := json.Marshal(d)
		if err != nil {
			appendError(buf, "failed to marshal device")
			c.AsyncWrite(buf.Bytes(), func(c gnet.Conn, err error) error {
				buf.Reset()
				bufPool.Put(buf)
				return nil
			})
			return
		}

		appendResponse(buf, "HTTP/1.1 201 Created", b, "Content-Type: application/json")
		c.AsyncWrite(buf.Bytes(), func(c gnet.Conn, err error) error {
			buf.Reset()
			bufPool.Put(buf)
			return nil
		})
	})

	if errors.Is(err, ants.ErrPoolOverload) {
		appendError(&hc.resp, "server is overload")
	}
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
	buf, _ := c.Peek(-1)
	n := len(buf)

pipeline:
	nextOffset, body, err := hc.parse(buf)
	hc.resetParser()
	if err != nil {
		goto response
	}
	if len(buf) < nextOffset { // incomplete request
		goto response
	}
	writeResponse(c, body)
	buf = buf[nextOffset:]
	if len(buf) > 0 {
		goto pipeline
	}
response:
	if hc.resp.Len() > 0 {
		c.Write(hc.resp.Bytes())
	}
	hc.reset()
	c.Discard(n - len(buf))
	return gnet.None
}

func appendError(buf *bytes.Buffer, msg string) {
	appendResponse(buf, "HTTP/1.1 500 Internal Server Error", msg, "Content-Type: text/plain; charset=utf-8")
}

func appendResponse[T []byte | string](buf *bytes.Buffer, startLine string, msg T, headers ...string) {
	buf.WriteString(startLine)
	buf.WriteString("\r\nServer: gnet\r\nDate: ")
	buf.WriteString(time.Now().Format("Mon, 02 Jan 2006 15:04:05 GMT"))
	buf.WriteString("\r\nContent-Length: ")
	buf.WriteString(strconv.Itoa(len(msg)))
	for _, header := range headers {
		buf.WriteString("\r\n")
		buf.WriteString(header)
	}
	buf.WriteString("\r\n\r\n")
	switch v := any(msg).(type) {
	case []byte:
		buf.Write(v)
	case string:
		buf.WriteString(v)
	}
}
