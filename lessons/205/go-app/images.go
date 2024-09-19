package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/prometheus/client_golang/prometheus"
)

// Image represents the image uploaded by the user.
type Image struct {

	// ImageUUID is the unique ID of the image.
	ImageUUID string

	// CreatedAt is the timestamp when the image was created.
	CreatedAt time.Time

	// Path to save the image.
	Key string
}

// NewImage creates a new image.
func NewImage() *Image {
	// Generate a new UUID for the image.
	id := uuid.New().String()

	// Record when the image was created.
	createdAt := time.Now()

	// Create an image with the generated ID and timestamp.
	image := &Image{
		ImageUUID: id,
		CreatedAt: createdAt,
		Key:       fmt.Sprintf("go-thumbnail-%s.png", id),
	}

	return image
}

// Save inserts a newly generated image into the Postgres database.
func (i *Image) save(ctx context.Context, tx pgx.Tx, m *metrics) (err error) {
	// Get the current time to record the duration of the request.
	now := time.Now()
	defer func() {
		if err == nil {
			// Record the duration of the insert query.
			m.duration.With(prometheus.Labels{"op": "db"}).Observe(time.Since(now).Seconds())
		}
	}()

	// Execute the query to create a new image record (pgx automatically prepares and caches statements by default).
	_, err = tx.Exec(ctx, `INSERT INTO "go_image" VALUES ($1, $2, $3)`, i.ImageUUID, i.Key, i.CreatedAt)
	return annotate(err, "dbpool.Exec failed")
}

// upload uploads S3 image to the bicket.
func upload(ctx context.Context, client *s3.Client, bucket string, key string, path string, m *metrics) (err error) {
	// Get the current time to record the duration of the request.
	now := time.Now()
	defer func() {
		if err == nil {
			// Record the duration of the request to S3.
			m.duration.With(prometheus.Labels{"op": "s3"}).Observe(time.Since(now).Seconds())
		}
	}()

	// Read the file from the local file system.
	file, err := os.Open(path)
	if err != nil {
		return annotate(err, "os.Open failed, path %s", path)
	}
	defer file.Close()

	// Prepare the request for the S3 bucket.
	input := &s3.PutObjectInput{
		Body:   file,
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	}

	// Upload the file to the S3 bucket.
	_, err = client.PutObject(ctx, input)
	return annotate(err, "client.PutObject failed")
}
