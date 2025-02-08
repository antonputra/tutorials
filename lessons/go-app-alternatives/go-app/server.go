package main

import (
	"github.com/bytedance/sonic"
)

var serializer = sonic.ConfigFastest

type server interface {
	serve(address string) error
}

type resp struct {
	Msg string `json:"msg"`
}

func newServer(cfg *Config) server {
	var s server
	switch cfg.Server {
	case "gin":
		s = newGinServer()
	case "fiber":
		s = newFiberServer()
	case "web":
		s = newWebServer()
	default:
		s = newStdServer()
	}

	return s
}
