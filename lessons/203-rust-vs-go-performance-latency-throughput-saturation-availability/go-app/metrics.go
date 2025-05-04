package main

import "github.com/prometheus/client_golang/prometheus"

// metrics represents Prometheus metrics.
type metrics struct {
	// A metric to record the duration of requests,
	// such as database queries or requests to the S3 object store.
	duration *prometheus.HistogramVec
}

// Create new metrics and register them with the Prometheus registry.
func NewMetrics(reg prometheus.Registerer) *metrics {
	// Unlike a Summary, buckets must be defined based on the expected application latency
	// to capture as many distributions as possible.
	buckets := []float64{0.001, 0.002, 0.003, 0.004, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045,
		0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.15, 0.2,
		0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95,
		1.0, 2.0, 3.0, 4.0, 5.0}

	// Create Prometheus metrics.
	m := &metrics{
		duration: prometheus.NewHistogramVec(prometheus.HistogramOpts{
			Namespace: "myapp",
			Name:      "request_duration_seconds",
			Help:      "Duration of the request.",
			Buckets:   buckets,
		}, []string{"op"}),
	}
	// Register metrics with Prometheus registry.
	reg.MustRegister(m.duration)

	return m
}
