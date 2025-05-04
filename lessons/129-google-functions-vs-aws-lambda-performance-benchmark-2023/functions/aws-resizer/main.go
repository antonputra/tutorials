package main

import (
	"bytes"
	"fmt"
	"image"
	"image/jpeg"
	"os"
	"time"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/disintegration/imaging"
)

func main() {
	lambda.Start(LambdaHandler)
}

func LambdaHandler() (int, error) {
	bucket := os.Getenv("BUCKET_NAME")
	key := "yosemite.jpg"
	width, height := 400, 400

	sess := session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
	}))

	image, err := getImage(bucket, key, sess)
	if err != nil {
		return 500, fmt.Errorf("failed to get s3 object: %v", err)
	}

	newImage, date := scaleImage(image, width, height)
	err = uploadImage(bucket, fmt.Sprintf("yosemite_%dx%d_%d.jpg", width, height, date.UnixMilli()), newImage, sess)
	if err != nil {
		return 500, fmt.Errorf("failed to save s3 object: %v", err)
	}
	return 200, nil
}

// getImage downloads image from S3.
func getImage(bucket string, key string, sess *session.Session) (image.Image, error) {
	svc := s3.New(sess)
	input := &s3.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	}
	output, err := svc.GetObject(input)
	if err != nil {
		return nil, err
	}

	image, _, err := image.Decode(output.Body)
	if err != nil {
		return nil, err
	}

	return image, nil
}

// uploadImage uploads image to S3.
func uploadImage(bucket string, key string, img image.Image, sess *session.Session) error {
	buf := new(bytes.Buffer)
	err := jpeg.Encode(buf, img, nil)
	if err != nil {
		return err
	}

	reader := bytes.NewReader(buf.Bytes())
	input := &s3.PutObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
		Body:   reader,
	}
	svc := s3.New(sess)
	_, err = svc.PutObject(input)
	if err != nil {
		return err
	}

	return nil
}

// scaleImage scales image using provided dimensions and returns last modified date.
func scaleImage(src image.Image, width int, height int) (image.Image, time.Time) {
	image := imaging.Resize(src, width, height, imaging.Lanczos)
	date := time.Now().UTC()
	return image, date
}
