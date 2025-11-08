package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func BenchmarkGetDevicesParallel(b *testing.B) {
	ms := &MyServer{}
	b.ReportAllocs()

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			req := httptest.NewRequest("GET", "/api/devices", nil)
			rec := httptest.NewRecorder()

			ms.getDevices(rec, req)

			res := rec.Result()
			if res.StatusCode != http.StatusOK {
				b.Fatalf("expected status %d, got %d", http.StatusOK, res.StatusCode)
			}
			res.Body.Close()
		}
	})
}
