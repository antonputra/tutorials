package main

import (
	"context"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/prometheus/client_golang/prometheus"
)

func getContext(tb testing.TB) context.Context {
	tb.Helper()

	ctx, done := context.WithCancel(context.Background())
	tb.Cleanup(done)
	return ctx
}

func setupServer(tb testing.TB, ctx context.Context) *httptest.Server {
	tb.Helper()

	ms := NewMyServer(ctx, &Config{}, prometheus.NewRegistry())

	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", ms.getHealth)
	mux.HandleFunc("GET /api/devices", ms.getDevices)

	srv := httptest.NewServer(mux)
	tb.Cleanup(srv.Close)
	srv.EnableHTTP2 = true

	return srv
}

func TestHeathcheck(t *testing.T) {
	srv := setupServer(t, getContext(t))

	res, err := http.Get(srv.URL + "/healthz")
	if err != nil {
		t.Fatalf("failed to get healthz: %v", err)
	}

	resBytes, err := io.ReadAll(res.Body)
	if err != nil {
		t.Errorf("failed to read body: %v", err)
	}

	if got, want := string(resBytes), "OK"; got != want {
		t.Errorf("bad healthz: got %q, want %q", got, want)
	}
}

func TestDevices(t *testing.T) {
	srv := setupServer(t, getContext(t))

	res, err := http.Get(srv.URL + "/api/devices")
	if err != nil {
		t.Fatalf("failed to get /api/devices: %v", err)
	}

	cType := res.Header.Get("Content-Type")
	if want := "application/json"; cType != want {
		t.Errorf("bad content-type: got %q, want %q", cType, want)
	}

	resBytes, err := io.ReadAll(res.Body)
	if err != nil {
		t.Errorf("failed to read body: %v", err)
	}

	want := `[` +
		`{"uuid":"b0e42fe7-31a5-4894-a441-007e5256afea","mac":"5F-33-CC-1F-43-82","firmware":"2.1.6"},` +
		`{"uuid":"0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7","mac":"EF-2B-C4-F5-D6-34","firmware":"2.1.5"},` +
		`{"uuid":"b16d0b53-14f1-4c11-8e29-b9fcef167c26","mac":"62-46-13-B7-B3-A1","firmware":"3.0.0"},` +
		`{"uuid":"51bb1937-e005-4327-a3bd-9f32dcf00db8","mac":"96-A8-DE-5B-77-14","firmware":"1.0.1"},` +
		`{"uuid":"e0a1d085-dce5-48db-a794-35640113fa67","mac":"7E-3B-62-A6-09-12","firmware":"3.5.6"}` +
		`]` + "\n"

	if got := string(resBytes); got != want {
		t.Errorf("mismatch: got %q, want %q", got, want)
	}
}

//go:generate go test -count 5 -bench . -benchmem -cpuprofile default.pgo

const benchmarkSize = 1000

func BenchmarkEndToEnd(b *testing.B) {
	ctx := getContext(b)
	srv := setupServer(b, ctx)

	client := &http.Client{}

	endpoints := []string{"/healthz", "/api/devices"}

	for _, endpoint := range endpoints {
		b.Run(endpoint[1:], func(b *testing.B) {
			url := srv.URL + endpoint
			for range b.N {
				for range benchmarkSize {
					res, err := client.Get(url)
					if err != nil {
						b.Fatalf("failed to get %s: %v", endpoint, err)
					}
					res.Body.Close()
				}
			}
		})
	}
}

func BenchmarkEndpoints(b *testing.B) {
	ctx := getContext(b)
	ms := NewMyServer(ctx, &Config{}, prometheus.NewRegistry())
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", ms.getHealth)
	mux.HandleFunc("GET /api/devices", ms.getDevices)

	endpoints := []string{"/healthz", "/api/devices"}

	for _, endpoint := range endpoints {
		b.Run(endpoint[1:], func(b *testing.B) {
			req := httptest.NewRequest("GET", endpoint, nil)
			for range b.N {
				for range benchmarkSize {
					res := httptest.NewRecorder()
					mux.ServeHTTP(res, req)
				}
			}
		})
	}
}
