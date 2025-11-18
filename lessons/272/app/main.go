package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/redis/go-redis/v9"
	"github.com/redis/go-redis/v9/maintnotifications"
)

var ctx = context.Background()

// payload for the Redis
type User struct {
	Handle      string `json:"handle"`
	Country     string `json:"country"`
	Timestamp   int64  `json:"timestamp"`
	Description string `json:"description"`
}

// String used to pad to ~512 bytes
const text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui kjdhf 13ye jasd sdhhu2edlka officia deserunt mollit anim id est laborum."

func main() {
	// Define flags.
	addr := flag.String("addr", "", "Redis address")
	rate := flag.Int("rate", 10, "Number of requests per second")
	pause := flag.Int("pause", 100, "Delays between requests in microseconds")

	// Parse the flags.
	flag.Parse()
	fmt.Printf("Connecting to %s, rate: %d, pause: %d\n", *addr, *rate, *pause)

	// Create Prometheus metrics.
	reg := prometheus.NewRegistry()
	m := mon.NewMetrics("client", []string{"version"}, []string{}, []string{"target"}, reg)
	mon.StartPrometheus(8082, reg)

	// Create Redis client.
	rdb := redis.NewClient(&redis.Options{
		Addr:     *addr,
		Password: "",
		DB:       0,
		MaintNotificationsConfig: &maintnotifications.Config{
			Mode: maintnotifications.ModeDisabled,
		},
	})

	// Set a 1-second TTL on the Redis keys.
	expr := time.Duration(time.Duration(1) * time.Second)

	// Initialize the start time and the counter to track the number of operations.
	var start time.Time = time.Now()
	var count int = 0

	// Start an infinite loop and perform the work.
	for {
		// Keep track of the time elapsed between each operation.
		end := time.Now()
		elapsed := end.Sub(start)

		// Reset the number of operations each second.
		if elapsed >= time.Second {
			start = time.Now()
			count = 0
		}

		// If the number of operations equals or exceeds the rate, sleep for the remaining time until the next second.
		// Sleeping avoids wasting CPU cycles, allowing for more efficient use of resources.
		if count >= *rate {
			next := time.Second - elapsed
			if next > time.Nanosecond {
				time.Sleep(next)
			}
		}

		// Use a UUID as the key.
		key := uuid.New()

		// Create a User for the Test.
		u := User{
			Handle:      "@antonvputra",
			Country:     "USA",
			Timestamp:   time.Now().UnixNano(),
			Description: text,
		}

		// Serialize the user to a string.
		value, err := json.Marshal(u)
		if err != nil {
			util.Warn(err, "rdb.Set failed")
			continue
		}

		// Set the Redis key (UUID) to the timestamp value.
		err = rdb.Set(ctx, key.String(), value, expr).Err()
		if err != nil {
			util.Warn(err, "rdb.Set failed")
			continue
		}

		// Fetch the timestamp by the UUID key.
		val, err := rdb.Get(ctx, key.String()).Result()
		if err != nil {
			util.Warn(err, "rdb.Get failed")
			continue
		}

		// Load the user from Redis
		var loaded User
		json.Unmarshal([]byte(val), &loaded)

		// Calculate the elapsed time between setting and retrieving the value in Redis.
		delta := time.Now().UnixNano() - loaded.Timestamp
		duration := time.Duration(delta)

		// Record the operation duration using a Prometheus histogram.
		m.Hist.WithLabelValues("redis").Observe(duration.Seconds())

		// Increment the operation counter.
		count++

		// Pause execution to prevent overloading the target.
		util.Sleep(*pause)
	}
}
