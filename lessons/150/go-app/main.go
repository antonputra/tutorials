package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/json"
	"encoding/pem"
	"fmt"

	"github.com/valyala/fasthttp"
)

type Keypair struct {
	Key string `json:"key"`
	Crt string `json:"crt"`
}

func main() {
	hl := func(ctx *fasthttp.RequestCtx) {
		switch string(ctx.Path()) {
		case "/api/keypair":
			getKeypair(ctx)
		case "/health":
			health(ctx)
		default:
			res := fmt.Sprintf("%s path is not supported", ctx.Path())
			ctx.Error(res, fasthttp.StatusNotFound)
		}
	}

	fasthttp.ListenAndServe(":8080", hl)
}

func getKeypair(ctx *fasthttp.RequestCtx) {
	switch string(ctx.Method()) {
	case "GET":
		key, cert, err := generateKeypair()
		kp := Keypair{Key: key, Crt: cert}
		if err != nil {
			fmt.Printf("generateKeypair failed %v", err)
			ctx.Error("failed to generate keypair", fasthttp.StatusInternalServerError)
			return
		}
		b, err := json.Marshal(kp)
		if err != nil {
			fmt.Printf("json.Marshal failed %v", err)
			ctx.Error("failed to generate keypair", fasthttp.StatusInternalServerError)
			return
		}
		ctx.SetBody(b)
	default:
		res := fmt.Sprintf("%s method is not supported", ctx.Method())
		ctx.Error(res, fasthttp.StatusMethodNotAllowed)
	}
}

func generateKeypair() (string, string, error) {
	bitSize := 2048

	// Generate RSA key.
	key, err := rsa.GenerateKey(rand.Reader, bitSize)
	if err != nil {
		return "", "", fmt.Errorf("rsa.GenerateKey failed %w", err)
	}

	// Extract public component.
	pub := key.Public()

	// Encode private key to PKCS#1 ASN.1 PEM.
	keyPEM := pem.EncodeToMemory(
		&pem.Block{
			Type:  "RSA PRIVATE KEY",
			Bytes: x509.MarshalPKCS1PrivateKey(key),
		},
	)

	// Encode public key to PKCS#1 ASN.1 PEM.
	pubPEM := pem.EncodeToMemory(
		&pem.Block{
			Type:  "RSA PUBLIC KEY",
			Bytes: x509.MarshalPKCS1PublicKey(pub.(*rsa.PublicKey)),
		},
	)

	return string(keyPEM), string(pubPEM), nil
}

func health(ctx *fasthttp.RequestCtx) {
	ctx.SetStatusCode(fasthttp.StatusOK)
}
