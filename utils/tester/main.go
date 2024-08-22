package main

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
	// Load app config from yaml file.
	var c Config
	c.loadConfig("config.yaml")

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

	for i, stage := range c.Stages {
		guard := make(chan struct{}, stage.Clients)
		now := time.Now()
		for {
			guard <- struct{}{}
			go func() {
				sendReq(m, client, c.RequestInterval, c.Url)
				<-guard
			}()
			if time.Since(now).Seconds() >= float64(stage.Interval*60) {
				fmt.Printf("Stage %d is finished\n", i)
				break
			}
		}
	}

}

// for {
// 	guard <- struct{}{}
// 	go func() {
// 		sendReq(m, client, c.RequestInterval, c.Url)
// 		<-guard
// 	}()
// 	if time.Since(now).Seconds() >= 1*60 {
// 		fmt.Println("Stage 1 is finished")
// 		break
// 	}
// }
