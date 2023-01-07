package main

import (
	"bytes"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"regexp"
	"strconv"
	"time"

	exporter "github.com/antonputra/tutorials/lessons/144/prometheus-nginx-exporter"
	"github.com/hpcloud/tail"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var exp = regexp.MustCompile(`^(?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<time>[^\]]*)\] \"(?P<method>\w+)(?:\s+(?P<path>[^\"]*?)(?:\s+\S*)?)?\" (?P<status_code>[^ ]*) (?P<size>[^ ]*)(?:\s"(?P<referer>[^\"]*)") "(?P<agent>[^\"]*)" (?P<urt>[^ ]*)$`)

type metrics struct {
	size     prometheus.Counter
	duration *prometheus.HistogramVec
	requests *prometheus.CounterVec
}

func NewMetrics(reg prometheus.Registerer) *metrics {
	m := &metrics{
		size: prometheus.NewCounter(prometheus.CounterOpts{
			Namespace: "nginx",
			Name:      "size_bytes_total",
			Help:      "Total bytes sent to the clients.",
		}),
		requests: prometheus.NewCounterVec(prometheus.CounterOpts{
			Namespace: "nginx",
			Name:      "http_requests_total",
			Help:      "Total number of requests.",
		}, []string{"status_code", "method", "path"}),
		duration: prometheus.NewHistogramVec(prometheus.HistogramOpts{
			Namespace: "nginx",
			Name:      "http_request_duration_seconds",
			Help:      "Duration of the request.",
			// Optionally configure time buckets
			Buckets: []float64{0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.0011, 0.0012, 0.0013, 0.0014, 0.0015, 0.0016, 0.0017, 0.0018, 0.0019, 0.002, 0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.5, 1, 2, 3, 4, 5},
			// Buckets: prometheus.DefBuckets,
		}, []string{"status_code", "method", "path"}),
	}
	reg.MustRegister(m.size, m.requests, m.duration)
	return m
}

func main() {
	var (
		targetHost = flag.String("target.host", "localhost", "nginx address with basic_status page")
		targetPort = flag.Int("target.port", 8080, "nginx port with basic_status page")
		targetPath = flag.String("target.path", "/status", "URL path to scrap metrics")
		promPort   = flag.Int("prom.port", 9150, "port to expose prometheus metrics")
		logPath    = flag.String("target.log", "/var/log/nginx/access.log", "path to access.log")
	)
	flag.Parse()

	uri := fmt.Sprintf("http://%s:%d%s", *targetHost, *targetPort, *targetPath)

	// Called on each collector.Collect.
	basicStats := func() ([]exporter.NginxStats, error) {
		var netClient = &http.Client{
			Timeout: time.Second * 10,
		}

		resp, err := netClient.Get(uri)
		if err != nil {
			log.Fatalf("netClient.Get failed %s: %s", uri, err)
		}
		defer resp.Body.Close()
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			log.Fatalf("io.ReadAll failed: %s", err)
		}
		r := bytes.NewReader(body)

		return exporter.ScanBasicStats(r)
	}

	// Make Prometheus client aware of our collectors.
	bc := exporter.NewBasicCollector(basicStats)

	reg := prometheus.NewRegistry()
	reg.MustRegister(bc)

	m := NewMetrics(reg)
	go tailAccessLogFile(m, *logPath)

	mux := http.NewServeMux()
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	mux.Handle("/metrics", promHandler)

	// Start listening for HTTP connections.
	port := fmt.Sprintf(":%d", *promPort)
	log.Printf("starting nginx exporter on %q/metrics", port)
	if err := http.ListenAndServe(port, mux); err != nil {
		log.Fatalf("cannot start nginx exporter: %s", err)
	}
}

func tailAccessLogFile(m *metrics, path string) {
	t, err := tail.TailFile(path, tail.Config{Follow: true, ReOpen: true})
	if err != nil {
		log.Fatalf("tail.TailFile failed: %s", err)
	}

	for line := range t.Lines {
		match := exp.FindStringSubmatch(line.Text)
		result := make(map[string]string)

		for i, name := range exp.SubexpNames() {
			if i != 0 && name != "" {
				result[name] = match[i]
			}
		}

		s, err := strconv.ParseFloat(result["size"], 64)
		if err != nil {
			continue
		}
		m.size.Add(s)

		m.requests.With(prometheus.Labels{"method": result["method"], "status_code": result["status_code"], "path": result["path"]}).Add(1)

		u, err := strconv.ParseFloat(result["urt"], 64)
		if err != nil {
			continue
		}
		m.duration.With(prometheus.Labels{"method": result["method"], "status_code": result["status_code"], "path": result["path"]}).Observe(u)

	}

}
