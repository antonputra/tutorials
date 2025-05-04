package main

import (
	"net/http"

	jsoniter "github.com/json-iterator/go"
)

// json - jsoniter object
var json = jsoniter.ConfigFastest

type server struct {
	cfg *Config
}

type resp struct {
	Msg string `json:"msg"`
}

func newServer(cfg *Config) *server {
	s := server{cfg: cfg}
	return &s
}

func renderJSON(w http.ResponseWriter, value any, status int) {
	enc := json.NewEncoder(w)
	enc.SetEscapeHTML(false)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := enc.Encode(value); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}
