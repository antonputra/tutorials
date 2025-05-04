package main

import (
	"io"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

// sendReq sends request to the server
func sendReq(m *metrics, client *http.Client, url string) {
	// Sleep to avoid sending requests at the same time.
	rn := rand.Intn(*scaleInterval)
	time.Sleep(time.Duration(rn) * time.Millisecond)

	// Get timestamp for histogram
	now := time.Now()

	// Send a request to the server
	res, err := client.Get(url)
	if err != nil {
		m.duration.With(prometheus.Labels{"path": url, "status": "500"}).Observe(time.Since(now).Seconds())
		log.Printf("client.Get failed: %v", err)
		return
	}
	// Read until the response is complete to reuse connection
	io.ReadAll(res.Body)

	// Close the body to reuse connection
	res.Body.Close()

	// Record request duration
	m.duration.With(prometheus.Labels{"path": url, "status": strconv.Itoa(res.StatusCode)}).Observe(time.Since(now).Seconds())
}
