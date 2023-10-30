package main

import (
	"context"
	"fmt"
	"io"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
)

// Image represents the image uploaded by the user.
type Image struct {
	// ImageUUID is the unique ID of the image.
	ImageUUID string

	// LastModified is the timestamp when the image was last modified.
	LastModified time.Time
}

// NewImage creates a new image.
func NewImage() *Image {
	// Generate a new UUID for the image.
	id := uuid.New().String()

	// Simulate the last modified date.
	lastModified := time.Now()

	// Create an image with the generated ID and timestamp.
	image := &Image{
		ImageUUID:    id,
		LastModified: lastModified,
	}

	return image
}

// Save inserts a newly generated image into the Postgres database.
func Save(c *Image, table string, dbpool *pgxpool.Pool, m *metrics, ctx context.Context) error {
	// Create a new CHILD span to record and trace the request.
	ctx, span := tracer.Start(ctx, "SQL INSERT")
	defer span.End()

	// Get the current time to record the duration of the request.
	now := time.Now()

	// Prepare the database query to insert a record.
	query := fmt.Sprintf("INSERT INTO %s VALUES ($1, $2)", table)

	// Execute the query to create a new image record.
	_, err := dbpool.Exec(context.Background(), query, c.ImageUUID, c.LastModified)
	if err != nil {
		return fmt.Errorf("dbpool.Exec failed: %w", err)
	}

	// Record the duration of the insert query.
	m.duration.With(prometheus.Labels{"op": "db"}).Observe(time.Since(now).Seconds())

	return nil
}

// download downloads S3 image and returns last modified date.
func download(sess *session.Session, bucket string, key string, m *metrics, ctx context.Context) (*time.Time, context.Context, error) {
	// Create a new CHILD span to record and trace the request.
	ctx, span := tracer.Start(ctx, "S3 GET")
	defer span.End()

	// Get the current time to record the duration of the request.
	now := time.Now()

	// Create a new S3 session.
	svc := s3.New(sess)

	// Prepare the request for the S3 bucket.
	input := &s3.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	}

	// Send the request to the S3 object store to download the image.
	output, err := svc.GetObject(input)
	if err != nil {
		return nil, nil, fmt.Errorf("svc.GetObject failed: %w", err)
	}

	// Read all the image bytes returned by AWS.
	_, err = io.ReadAll(output.Body)
	if err != nil {
		return nil, nil, fmt.Errorf("io.ReadAll failed: %w", err)
	}

	// Record the duration of the request to S3.
	m.duration.With(prometheus.Labels{"op": "s3"}).Observe(time.Since(now).Seconds())

	return output.LastModified, ctx, nil
}
