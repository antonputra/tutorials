package main

import (
	"io"
	"log/slog"
	"net/http"
	"time"

	"github.com/antonputra/go-utils/util"
	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
)

func (s *server) getHealth(w http.ResponseWriter, req *http.Request) {
	io.WriteString(w, "OK")
}

func (s *server) getDevices(w http.ResponseWriter, req *http.Request) {
	device := []Device{
		{
			Id:        1,
			Uuid:      "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
			Mac:       "EF-2B-C4-F5-D6-34",
			Firmware:  "2.1.5",
			CreatedAt: "2024-05-28T15:21:51.137Z",
			UpdatedAt: "2024-05-28T15:21:51.137Z",
		},
		{
			Id:        2,
			Uuid:      "d2293412-36eb-46e7-9231-af7e9249fffe",
			Mac:       "E7-34-96-33-0C-4C",
			Firmware:  "1.0.3",
			CreatedAt: "2024-01-28T15:20:51.137Z",
			UpdatedAt: "2024-01-28T15:20:51.137Z",
		},
		{
			Id:        3,
			Uuid:      "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
			Mac:       "68-93-9B-B5-33-B9",
			Firmware:  "4.3.1",
			CreatedAt: "2024-08-28T15:18:21.137Z",
			UpdatedAt: "2024-08-28T15:18:21.137Z",
		},
	}

	renderJSON(w, &device, 200)
}

func (s *server) saveDevice(w http.ResponseWriter, req *http.Request) {
	ctx := req.Context()

	decoder := json.NewDecoder(req.Body)
	d := new(Device)
	err := decoder.Decode(&d)
	if err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "decode", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to decode device")
		renderJSON(w, resp{Msg: "failed to decode device"}, 400)
		return
	}

	// to match elixir
	now := time.Now().Format(time.RFC3339Nano)
	d.Uuid = uuid.New().String()
	d.CreatedAt = now
	d.UpdatedAt = now

	err = d.insert(ctx, s.db, s.m)
	if err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
		util.Warn(err, "failed to save device in postgres")
		renderJSON(w, resp{Msg: "failed to save device in postgres"}, 400)
		return
	}
	slog.Debug("device saved in postgres", "id", d.Id, "mac", d.Mac, "firmware", d.Firmware)

	err = d.set(s.cache, s.m, s.cfg.CacheConfig.Expiration)
	if err != nil {
		s.m.Errors.With(prometheus.Labels{"op": "set", "db": "memcache"}).Add(1)
		util.Warn(err, "failed to save device in memcache")
		renderJSON(w, resp{Msg: "failed to save device in memcache"}, 400)
		return
	}

	renderJSON(w, &d, 201)
}
