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
func (i *Image) save(ctx context.Context, dbpool *pgxpool.Pool) error {
	// Execute the query to create a new image record (pgx automatically prepares and caches statements by default).
	_, err := dbpool.Exec(ctx, "INSERT INTO go_image VALUES ($1, $2, $3)", i.ImageUUID, i.Key, i.CreatedAt)
	if err != nil {
		return fmt.Errorf("dbpool.Exec failed: %w", err)
	}

	return nil
}

// upload uploads S3 image to the bicket.
func upload(ctx context.Context, client *s3.Client, bucket string, key string, path string) error {
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
	_, err = client.PutObject(ctx, input)
	if err != nil {
		return fmt.Errorf("svc.PutObject failed: %w", err)
	}

	return nil
}
