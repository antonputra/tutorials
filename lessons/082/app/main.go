package main

import (
	"flag"
	"fmt"
	"html"
	"log"
	"net/http"
	"strconv"
)

func main() {
	name := flag.String("name", "", "service name")
	port := flag.Int("port", 0, "port number")
	flag.Parse()

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		log.Printf("Method: %s", r.Method)
		log.Printf("Protocol: %s", r.Proto)
		log.Printf("Headers: %v", r.Header)
		fmt.Fprintf(w, "Hello from %s, resource: %q\n", *name, html.EscapeString(r.URL.Path))
	})

	log.Printf("Service %s, running on port %d", *name, *port)
	log.Fatal(http.ListenAndServe(":"+strconv.Itoa(*port), nil))
}
