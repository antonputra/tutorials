package main

import "github.com/prometheus/client_golang/prometheus"

// metrics represents Prometheus metrics.
type metrics struct {
	// A metric to record the duration of requests,
	// such as database queries or requests to the S3 object store.
	duration *prometheus.HistogramVec
}

// Unlike a Summary, buckets must be defined based on the expected application latency to capture as many distributions as possible.
// More buckets mean more load on your monitoring system, so adapt to your app!!!
var buckets = []float64{
	0.0001, 0.00015, 0.0002, 0.00025, 0.0003, 0.00035, 0.0004, 0.00045, 0.0005, 0.00055, 0.0006, 0.00065, 0.0007, 0.00075, 0.0008, 0.00085, 0.0009, 0.00095,
	0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.0065, 0.007, 0.0075, 0.008, 0.0085, 0.009, 0.0095,
	0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095,
	0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95,
	1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
}

// Create new metrics and register them with the Prometheus registry.
func NewMetrics(reg prometheus.Registerer) *metrics {

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
