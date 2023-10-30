package main

import (
	"flag"
	"log"
	"math/rand"
	"net/http"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	maxClients    = flag.Int("maxClients", 100, "Maximum number of virtual clients")
	scaleInterval = flag.Int("scaleInterval", 1, "Scale interval in milliseconds")
	randomSleep   = flag.Int("randomSleep", 1000, "Random sleep from 0 to target microseconds")
	target        = flag.String("target", "locahost", "Target URL for the first server")
)

func main() {
	// Sleep for 5 seconds before running test
	time.Sleep(5 * time.Second)

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
						wg.Done()
						return
					}
					sendReq(m, client, url)
				}
			}()
		}

		doWork(ch, clients)

		// Sleep for one second and increase number of clients
		time.Sleep(time.Duration(*scaleInterval) * time.Millisecond)
	}
}

func doWork(ch chan string, clients int) {
	if clients == *maxClients {
		for {
			ch <- *target
			sleep(*randomSleep)
		}
	}

	for i := 0; i < clients; i++ {
		ch <- *target
		sleep(*randomSleep)
	}
}

func sleep(us int) {
	r := rand.Intn(us)
	time.Sleep(time.Duration(r) * time.Microsecond)
}
