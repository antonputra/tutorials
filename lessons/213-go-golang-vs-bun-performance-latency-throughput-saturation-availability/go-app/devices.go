package main

import (
	"context"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"go.mongodb.org/mongo-driver/mongo"
)

// Device represents hardware device
type Device struct {

	// Universally unique identifier
	UUID string `json:"uuid"`

	// Mac address
	Mac string `json:"mac"`

	// Firmware version
	Firmware string `json:"firmware"`
}

// Save inserts a Device into the MongoDb database.
func (d *Device) Save(ctx context.Context, db *mongo.Database, m *metrics) (err error) {
	// Get the current time to record the duration of the request.
	now := time.Now()
	defer func() {
		if err == nil {
			// Record the duration of the insert query.
			m.duration.With(prometheus.Labels{"op": "db"}).Observe(time.Since(now).Seconds())
		}
	}()

	_, err = db.Collection("go_devices").InsertOne(ctx, d)
	return annotate(err, "db.Exec failed")
}
