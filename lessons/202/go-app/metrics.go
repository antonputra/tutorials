package main

import "github.com/prometheus/client_golang/prometheus"

// metrics represents Prometheus metrics.
type metrics struct {
	// A metric to record the duration of requests,
	// such as database queries or requests to the S3 object store.
	duration *prometheus.SummaryVec
}

// Create new metrics and register them with the Prometheus registry.
func NewMetrics(reg prometheus.Registerer) *metrics {
	// Create Prometheus metrics.
	m := &metrics{
		duration: prometheus.NewSummaryVec(prometheus.SummaryOpts{
			Namespace:  "myapp",
			Name:       "request_duration_seconds",
			Help:       "Duration of the request.",
			Objectives: map[float64]float64{0.9: 0.01, 0.99: 0.001},
		}, []string{"op"}),
	}
	// Register metrics with Prometheus registry.
	reg.MustRegister(m.duration)

	return m
}
