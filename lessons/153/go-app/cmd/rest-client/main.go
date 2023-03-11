package main

import (
	"flag"
	"io"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	maxClients    = flag.Int("maxClients", 100, "Maximum number of virtual clients")
	scaleInterval = flag.Int("scaleInterval", 1, "Scale interval in milliseconds")
	target1       = flag.String("target1", "locahost", "Target URL for the first server")
	target2       = flag.String("target2", "locahost", "Target URL for the second server")
)

type metrics struct {
	duration *prometheus.SummaryVec
}

func NewMetrics(reg prometheus.Registerer) *metrics {
	m := &metrics{
		duration: prometheus.NewSummaryVec(prometheus.SummaryOpts{
			Namespace:  "tester",
			Name:       "duration_seconds",
			Help:       "Duration of the request.",
			Objectives: map[float64]float64{0.9: 0.01, 0.99: 0.001},
		}, []string{"path", "status"}),
	}
	reg.MustRegister(m.duration)
	return m
}

func main() {
	// Parse the command line into the defined flags
	flag.Parse()

	// Create Prometheus registry
	reg := prometheus.NewRegistry()
	m := NewMetrics(reg)

	// Create Prometheus HTTP server to expose metrics
	pMux := http.NewServeMux()
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	pMux.Handle("/metrics", promHandler)

	go func() {
		log.Fatal(http.ListenAndServe(":8081", pMux))
	}()

	// Create transport and client to reuse connection pool
	tr := &http.Transport{}
	client := &http.Client{Transport: tr}

	// Create job queue
	var ch = make(chan string, *maxClients*2)
	var wg sync.WaitGroup

	// Slowly increase the number of virtual clients
	for clients := 0; clients <= *maxClients; clients++ {
		wg.Add(1)

		for i := 0; i < clients; i++ {
			go func() {
				for {
					url, ok := <-ch
					if !ok {
						// TODO: Fix negative counter
						wg.Done()
						return
					}
					sendReq(m, client, url)
				}
			}()
		}

		for i := 0; i < clients; i++ {
			ch <- *target1
			ch <- *target2
		}
		// TODO: make it dynamic
		// Sleep for one second and increase number of clients
		time.Sleep(time.Duration(*scaleInterval) * time.Millisecond)
	}

	// Wait for Prometheus to scrape metrics
	log.Println("Test is done!")
	select {}

	// Close the channel
	// close(ch)
	// Block until the WaitGroup counter goes back to 0
	// wg.Wait()
}

// sendReq sends requests to the server
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

	// Close the body to reuse connections
	res.Body.Close()

	// Record request duration
	m.duration.With(prometheus.Labels{"path": url, "status": strconv.Itoa(res.StatusCode)}).Observe(time.Since(now).Seconds())
}
