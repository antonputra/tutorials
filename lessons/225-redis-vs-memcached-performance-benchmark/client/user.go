package main

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/bradfitz/gomemcache/memcache"
	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/redis/rueidis"
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
		Username:  getString(10),
		FirstName: getString(5),
		LastName:  getString(10),
		Address:   getString(20),
	}

	return &u
}

func (u *User) SaveToMC(mc *memcache.Client, m *metrics, exp int32, debug bool) (err error) {
	b, err := json.Marshal(u)
	if err != nil {
		return annotate(err, "json.Marshal failed")
	}

	now := time.Now()
	err = mc.Set(&memcache.Item{Key: u.Uuid, Value: b, Expiration: exp})
	if err != nil {
		return annotate(err, "mc.Set failed")
	}
	m.duration.With(prometheus.Labels{"op": "set", "db": "memcache"}).Observe(time.Since(now).Seconds())

	if debug {
		fmt.Printf("item saved in memcache, key: %s, value: %s\n", u.Uuid, string(b))
	}

	return nil
}

func (u *User) GetFromMC(mc *memcache.Client, m *metrics, debug bool) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"op": "get", "db": "memcache"}).Observe(time.Since(now).Seconds())
		}
	}()

	it, err := mc.Get(u.Uuid)
	if err != nil {
		return annotate(err, "mc.Get failed")
	}

	if debug {
		user := User{}
		err := json.Unmarshal(it.Value, &user)
		fail(err, "json.Unmarshal")
		fmt.Printf("item fetched from memcache: %+v\n", user)
	}

	return nil
}

func (u *User) SaveToRedis(ctx context.Context, rdb rueidis.Client, m *metrics, exp int32, debug bool) (err error) {
	b, err := json.Marshal(u)
	if err != nil {
		return annotate(err, "json.Marshal failed")
	}

	expr := time.Duration(time.Duration(exp) * time.Second)
	now := time.Now()
	err = rdb.Do(ctx, rdb.B().Set().Key(u.Uuid).Value(rueidis.BinaryString(b)).Ex(expr).Build()).Error()
	if err != nil {
		return annotate(err, "rdb.Set failed")
	}
	m.duration.With(prometheus.Labels{"op": "set", "db": "redis"}).Observe(time.Since(now).Seconds())

	if debug {
		fmt.Printf("item saved in redis, key: %s, value: %s\n", u.Uuid, string(b))
	}

	return nil
}

func (u *User) GetFromRedis(ctx context.Context, rdb rueidis.Client, m *metrics, debug bool) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"op": "get", "db": "redis"}).Observe(time.Since(now).Seconds())
		}
	}()

	it, err := rdb.Do(ctx, rdb.B().Get().Key(u.Uuid).Build()).ToString()
	if err != nil {
		return annotate(err, "mc.Get failed")
	}

	if debug {
		fmt.Printf("item fetched from redis: %+v\n", it)
	}

	return nil
}
