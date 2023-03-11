package serverless

import (
	"bytes"
	"context"
	"fmt"
	"image"
	"image/jpeg"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"cloud.google.com/go/storage"
	"github.com/GoogleCloudPlatform/functions-framework-go/functions"
	"github.com/disintegration/imaging"
)

func init() {
	functions.HTTP("Resizer", Resizer)
}

func Resizer(w http.ResponseWriter, r *http.Request) {
	bucket := os.Getenv("BUCKET_NAME")
	key := "yosemite.jpg"
	width, height := 400, 400

	ctx := context.Background()
	image, err := getImage(bucket, key, ctx)
	if err != nil {
		log.Printf("failed to get image: %v", err)
		http.Error(w, "server error", http.StatusInternalServerError)
		return
	}

	newImage, date := scaleImage(image, width, height)
	err = uploadImage(bucket, fmt.Sprintf("yosemite_%dx%d_%d.jpg", width, height, date.UnixMilli()), newImage, ctx)
	if err != nil {
		log.Printf("failed to upload image: %v", err)
		http.Error(w, "server error", http.StatusInternalServerError)
		return
	}
	fmt.Fprintf(w, "OK")
}

// getImage downloads image from GS.
func getImage(bucket string, key string, ctx context.Context) (image.Image, error) {
	client, err := storage.NewClient(ctx)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}
	defer client.Close()

	rc, err := client.Bucket(bucket).Object(key).NewReader(ctx)
	if err != nil {
		log.Fatalln(err)
	}
	defer rc.Close()

	image, _, err := image.Decode(rc)
	if err != nil {
		return nil, err
	}

	return image, nil
}

// uploadImage uploads image to GS.
func uploadImage(bucket string, key string, img image.Image, ctx context.Context) error {
	client, err := storage.NewClient(ctx)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}
	defer client.Close()

	buf := new(bytes.Buffer)
	err = jpeg.Encode(buf, img, nil)
	if err != nil {
		return err
	}

	reader := bytes.NewReader(buf.Bytes())
	o := client.Bucket(bucket).Object(key)
	wc := o.NewWriter(ctx)
	if _, err = io.Copy(wc, reader); err != nil {
		return err
	}
	if err := wc.Close(); err != nil {
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
