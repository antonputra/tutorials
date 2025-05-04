package exporter

import (
	"bufio"
	"fmt"
	"io"
	"strconv"
	"strings"
)

// NginxStats nginx basic stats
type NginxStats struct {
	// Nginx active connections
	ConnectionsActive float64

	// Connections (Reading - Writing - Waiting)
	Connections []Connections
}

type Connections struct {
	// Type is one of (Reading - Writing - Waiting)
	Type string

	// Total number of connections
	Total float64
}

// ScanBasicStats scans and parses nginx basic stats
func ScanBasicStats(r io.Reader) ([]NginxStats, error) {
	s := bufio.NewScanner(r)

	var stats []NginxStats
	var conns []Connections
	var nginxStats NginxStats

	for s.Scan() {

		fields := strings.Fields(string(s.Bytes()))

		if len(fields) == 3 && fields[0] == "Active" {
			c, err := strconv.ParseFloat(fields[2], 64)
			if err != nil {
				return nil, fmt.Errorf("%w: strconv.ParseFloat failed", err)
			}
			nginxStats.ConnectionsActive = c
		}

		if fields[0] == "Reading:" {
			// Fake metrics
			readingConns := Connections{Type: "reading", Total: 67}
			writingConns := Connections{Type: "writing", Total: 81}
			waitingConns := Connections{Type: "waiting", Total: 100}

			conns = append(conns, readingConns, writingConns, waitingConns)
			nginxStats.Connections = conns
		}

	}

	stats = append(stats, nginxStats)

	if err := s.Err(); err != nil {
		return nil, fmt.Errorf("%w: failed to read metrics", err)
	}

	return stats, nil
}
