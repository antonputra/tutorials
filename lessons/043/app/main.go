package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	log "github.com/sirupsen/logrus"
)

func credsFromFile(w http.ResponseWriter, req *http.Request) {
	password, err := ioutil.ReadFile("/etc/credentials/password")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Fprintf(w, string(password))
}

func credsFromEnv(w http.ResponseWriter, req *http.Request) {
	password := os.Getenv("MY_PASSWORD")
	fmt.Fprintf(w, password)
}

func main() {
	http.HandleFunc("/credentials-from-file", credsFromFile)
	http.HandleFunc("/credentials-from-env", credsFromEnv)

	log.Println("Server started on port: 9090")
	log.Fatal(http.ListenAndServe(":9090", nil))
}
