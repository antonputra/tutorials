package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

type metrics struct {
	clients  prometheus.Gauge
	duration *prometheus.HistogramVec
}

// Unlike a Summary, buckets must be defined based on the expected application latency to capture as many distributions as possible.
// More buckets mean more load on your monitoring system, so adapt to your app!!!
var buckets = []float64{
	0.00001, 0.000015, 0.00002, 0.000025, 0.00003, 0.000035, 0.00004, 0.000045,
	0.00005, 0.000055, 0.00006, 0.000065, 0.00007, 0.000075, 0.00008, 0.000085,
	0.00009, 0.000095, 0.0001, 0.000101, 0.000102, 0.000103, 0.000104, 0.000105,
	0.000106, 0.000107, 0.000108, 0.000109, 0.00011, 0.000111, 0.000112, 0.000113,
	0.000114, 0.000115, 0.000116, 0.000117, 0.000118, 0.000119, 0.00012, 0.000121,
	0.000122, 0.000123, 0.000124, 0.000125, 0.000126, 0.000127, 0.000128,
	0.000129, 0.00013, 0.000131, 0.000132, 0.000133, 0.000134, 0.000135, 0.000136,
	0.000137, 0.000138, 0.000139, 0.00014, 0.000141, 0.000142, 0.000143, 0.000144,
	0.000145, 0.000146, 0.000147, 0.000148, 0.000149, 0.00015, 0.000151, 0.000152,
	0.000153, 0.000154, 0.000155, 0.000156, 0.000157, 0.000158, 0.000159, 0.00016,
	0.000161, 0.000162, 0.000163, 0.000164, 0.000165, 0.000166, 0.000167,
	0.000168, 0.000169, 0.00017, 0.000171, 0.000172, 0.000173, 0.000174, 0.000175,
	0.000176, 0.000177, 0.000178, 0.000179, 0.00018, 0.000181, 0.000182, 0.000183,
	0.000184, 0.000185, 0.000186, 0.000187, 0.000188, 0.000189, 0.00019, 0.000191,
	0.000192, 0.000193, 0.000194, 0.000195, 0.000196, 0.000197, 0.000198,
	0.000199, 0.0002, 0.00021, 0.00022, 0.00023, 0.00024, 0.00025, 0.00026,
	0.00027, 0.00028, 0.00029, 0.0003, 0.00031, 0.00032, 0.00033, 0.00034,
	0.00035, 0.00036, 0.00037, 0.00038, 0.00039, 0.0004, 0.00041, 0.00042,
	0.00043, 0.00044, 0.00045, 0.00046, 0.00047, 0.00048, 0.00049, 0.0005,
	0.00051, 0.00052, 0.00053, 0.00054, 0.00055, 0.00056, 0.00057, 0.00058,
	0.00059, 0.0006, 0.00061, 0.00062, 0.00063, 0.00064, 0.00065, 0.00066,
	0.00067, 0.00068, 0.00069, 0.0007, 0.00071, 0.00072, 0.00073, 0.00074,
	0.00075, 0.00076, 0.00077, 0.00078, 0.00079, 0.0008, 0.00081, 0.00082,
	0.00083, 0.00084, 0.00085, 0.00086, 0.00087, 0.00088, 0.00089, 0.0009,
	0.00091, 0.00092, 0.00093, 0.00094, 0.00095, 0.00096, 0.00097, 0.00098,
	0.00099, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005,
	0.0055, 0.006, 0.0065, 0.007, 0.0075, 0.008, 0.0085, 0.009, 0.0095, 0.01,
	0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07,
	0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
	0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.5, 2.0, 2.5,
	3.0, 3.5, 4.0, 4.5, 5.0,
}

func NewMetrics(reg prometheus.Registerer) *metrics {
	m := &metrics{
		clients: prometheus.NewGauge(prometheus.GaugeOpts{
			Namespace: "tester",
			Name:      "active_clients",
			Help:      "Number of active clients.",
		}),
		duration: prometheus.NewHistogramVec(prometheus.HistogramOpts{
			Namespace: "tester",
			Name:      "request_duration_seconds",
			Help:      "Duration of the request.",
			Buckets:   buckets,
		}, []string{"operation", "method"}),
	}
	reg.MustRegister(m.duration, m.clients)

	return m
}

func StartPrometheusServer(c *Config, reg *prometheus.Registry) {
	pMux := http.NewServeMux()
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	pMux.Handle("/metrics", promHandler)

	// Start an HTTP server to expose Prometheus metrics in the background.
	metricsPort := fmt.Sprintf(":%d", c.MetricsPort)
	go func() {
		log.Printf("Starting the Prometheus server on port %d", c.MetricsPort)
		log.Fatal(http.ListenAndServe(metricsPort, pMux))
	}()
}
