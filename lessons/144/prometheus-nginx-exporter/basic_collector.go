package exporter

import (
	"github.com/prometheus/client_golang/prometheus"
)

var _ prometheus.Collector = &basicCollector{}

// A basicCollector is a prometheus.Collector for nginx stats.
type basicCollector struct {
	// Nginx active connections
	ConnectionsActive *prometheus.Desc

	// Connections (Reading - Writing - Waiting)
	Connections *prometheus.Desc

	// A parameterized function used to gather metrics.
	stats func() ([]NginxStats, error)
}

// NewBasicCollector constructs a collector using a stats function.
func NewBasicCollector(stats func() ([]NginxStats, error)) prometheus.Collector {
	return &basicCollector{
		ConnectionsActive: prometheus.NewDesc(
			"nginx_connections_active",
			"Number of active connections.",
			[]string{},
			nil,
		),
		Connections: prometheus.NewDesc(
			"nginx_connections_total",
			"Connections (Reading - Writing - Waiting)",
			[]string{"type"},
			nil,
		),
		stats: stats,
	}
}

// Describe implements prometheus.Collector.
func (c *basicCollector) Describe(ch chan<- *prometheus.Desc) {
	// Gather metadata about each metric.
	ds := []*prometheus.Desc{
		c.ConnectionsActive,
	}
	for _, d := range ds {
		ch <- d
	}
}

// Collect implements prometheus.Collector.
func (c *basicCollector) Collect(ch chan<- prometheus.Metric) {
	// Take a stats snapshot. Must be concurrency safe.
	stats, err := c.stats()
	if err != nil {
		// If an error occurs, send an invalid metric to notify
		// Prometheus of the problem.
		ch <- prometheus.NewInvalidMetric(c.ConnectionsActive, err)
		return
	}
	for _, s := range stats {
		ch <- prometheus.MustNewConstMetric(
			c.ConnectionsActive,
			prometheus.GaugeValue,
			s.ConnectionsActive,
		)
		for _, conn := range s.Connections {
			conns := []struct {
				connType string
				total    float64
			}{
				{connType: conn.Type, total: conn.Total},
			}
			for _, connT := range conns {
				ch <- prometheus.MustNewConstMetric(
					c.Connections,
					prometheus.CounterValue,
					connT.total,
					connT.connType,
				)
			}
		}
	}
}
