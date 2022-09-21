package main

import (
	"io/ioutil"
	"math/rand"
	"os"
	"time"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/s3"
)

func main() {
	lambda.Start(LambdaHandler)
}

func LambdaHandler() (int, error) {
	bucket := os.Getenv("BUCKET_NAME")
	key := "thumbnail.png"
	tableName := "images"

	sess := session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
	}))

	date, err := getS3Object(bucket, key, sess)
	if err != nil {
		return 500, err
	}
	newDate := getNewDate(date)

	err = saveLastModified(tableName, newDate, sess)
	if err != nil {
		return 500, err
	}
	return 200, nil
}

// getS3Object downloads S3 object and returns last modified date in UTC format.
func getS3Object(bucket string, key string, sess *session.Session) (*time.Time, error) {
	svc := s3.New(sess)
	input := &s3.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	}
	output, err := svc.GetObject(input)
	if err != nil {
		return nil, err
	}
	_, err = ioutil.ReadAll(output.Body)
	if err != nil {
		return nil, err
	}
	return output.LastModified, nil
}

// saveLastModified saves the last modified date to the DynamoDB table.
func saveLastModified(tableName string, date string, sess *session.Session) error {
	svc := dynamodb.New(sess)
	input := &dynamodb.PutItemInput{
		Item: map[string]*dynamodb.AttributeValue{
			"last_modified_date": {
				S: aws.String(date),
			},
		},
		TableName: aws.String(tableName),
	}
	_, err := svc.PutItem(input)
	if err != nil {
		return err
	}
	return nil
}

// getNewDate generates new random date.
func getNewDate(date *time.Time) string {
	seed := rand.NewSource(time.Now().UnixNano())
	rand := rand.New(seed)
	randomNumberOfDays := rand.Intn(10000)
	return date.AddDate(0, 0, randomNumberOfDays).String()
}
