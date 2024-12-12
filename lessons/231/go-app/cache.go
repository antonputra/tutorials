package main

import (
	"fmt"

	"github.com/bradfitz/gomemcache/memcache"
)

func cacheConnect(cfg *Config) *memcache.Client {
	mc := memcache.New(fmt.Sprintf("%s:11211", cfg.CacheConfig.Host))

	return mc
}
