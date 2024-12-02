package main

import (
	"context"
	"encoding/json"
	"log/slog"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"

	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/redis/go-redis/v9"
)

type User struct {
	Uuid      string `json:"uuid"`
	Username  string `json:"username"`
	FirstName string `json:"firstName"`
	LastName  string `json:"lastName"`
	Address   string `json:"address"`
}

func NewUser() *User {
	id := uuid.New()

	u := User{
		Uuid:      id.String(),
		Username:  util.GenString(10),
		FirstName: util.GenString(5),
		LastName:  util.GenString(10),
		Address:   util.GenString(20),
	}

	return &u
}

func (u *User) set(ctx context.Context, rdb *redis.Client, m *mon.Metrics, exp int32) (err error) {
	b, err := json.Marshal(u)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "set", "db": "redis"}).Add(1)
		return util.Annotate(err, "json.Marshal failed")
	}

	expr := time.Duration(time.Duration(exp) * time.Second)
	now := time.Now()
	err = rdb.Set(ctx, u.Uuid, b, expr).Err()
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "set", "db": "redis"}).Add(1)
		return util.Annotate(err, "rdb.Set failed")
	}
	m.Duration.With(prometheus.Labels{"op": "set", "db": "redis"}).Observe(time.Since(now).Seconds())

	slog.Debug("item saved in redis", "key", u.Uuid, "value", b)

	return nil
}

func (u *User) cset(ctx context.Context, rdb *redis.ClusterClient, m *mon.Metrics, exp int32) (err error) {
	b, err := json.Marshal(u)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "set", "db": "redis"}).Add(1)
		return util.Annotate(err, "json.Marshal failed")
	}

	expr := time.Duration(time.Duration(exp) * time.Second)
	now := time.Now()
	err = rdb.Set(ctx, u.Uuid, b, expr).Err()
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "set", "db": "redis"}).Add(1)
		return util.Annotate(err, "rdb.Set failed")
	}
	m.Duration.With(prometheus.Labels{"op": "set", "db": "redis"}).Observe(time.Since(now).Seconds())

	slog.Debug("item saved in redis", "key", u.Uuid, "value", b)

	return nil
}

func (u *User) get(ctx context.Context, rdb *redis.Client, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "get", "db": "redis"}).Observe(time.Since(now).Seconds())
		}
	}()

	it, err := rdb.Get(ctx, u.Uuid).Result()
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "get", "db": "redis"}).Add(1)
		return util.Annotate(err, "mc.Get failed")
	}
	slog.Debug("item fetched from redis", "item", it)

	return nil
}

func (u *User) cget(ctx context.Context, rdb *redis.ClusterClient, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "get", "db": "redis"}).Observe(time.Since(now).Seconds())
		}
	}()

	it, err := rdb.Get(ctx, u.Uuid).Result()
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "get", "db": "redis"}).Add(1)
		return util.Annotate(err, "mc.Get failed")
	}
	slog.Debug("item fetched from redis", "item", it)

	return nil
}
