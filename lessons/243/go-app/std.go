package main

import (
	"log"
	"net/http"
)

type stdServer struct {
	mux http.Handler
}

func newStdServer() *stdServer {
	s := stdServer{
		mux: getMux(),
	}
	return &s
}

func getMux() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/devices", handler)
	return mux
}

func renderJSON(w http.ResponseWriter, value any, status int) {
	enc := serializer.NewEncoder(w)
	enc.SetEscapeHTML(false)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := enc.Encode(value); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func handler(w http.ResponseWriter, req *http.Request) {
	renderJSON(w, getDevices(), http.StatusOK)
}

func (s *stdServer) serve(address string) error {
	log.Printf("Starting std server on port %s", address)
	return http.ListenAndServe(address, s.mux)
}
