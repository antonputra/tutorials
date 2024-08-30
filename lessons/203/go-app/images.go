package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
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
func save(c *Image, table string, dbpool *pgxpool.Pool, m *metrics) error {
	// Get the current time to record the duration of the request.
	now := time.Now()

	// Prepare the database query to insert a record (unsafe).
	query := fmt.Sprintf("INSERT INTO %s VALUES ($1, $2, $3)", table)

	// Execute the query to create a new image record (pgx automatically prepares and caches statements by default).
	_, err := dbpool.Exec(context.Background(), query, c.ImageUUID, c.Key, c.CreatedAt)
	if err != nil {
		return fmt.Errorf("dbpool.Exec failed: %w", err)
	}

	// Record the duration of the insert query.
	m.duration.With(prometheus.Labels{"op": "db"}).Observe(time.Since(now).Seconds())

	return nil
}

// upload uploads S3 image to the bicket.
func upload(client *s3.Client, bucket string, key string, path string, m *metrics) error {
	// Get the current time to record the duration of the request.
	now := time.Now()

	// Read the file from the local file system.
	file, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("os.Open failed, path %s: %w", path, err)
	}
	defer file.Close()

	// Prepare the request for the S3 bucket.
	input := &s3.PutObjectInput{
		Body:   file,
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	}

	// Upload the file to the S3 bucket.
	_, err = client.PutObject(context.TODO(), input)
	if err != nil {
		return fmt.Errorf("svc.PutObject failed: %w", err)
	}

	// Record the duration of the request to S3.
	m.duration.With(prometheus.Labels{"op": "s3"}).Observe(time.Since(now).Seconds())

	return nil
}
