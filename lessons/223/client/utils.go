package main

import (
	"fmt"
	"log"
	"math/rand"
	"time"
)

func random(min int64, max int64) int64 {
	return rand.Int63n(max-min) + min
}

func sleep(us int) {
	r := rand.Intn(us)
	time.Sleep(time.Duration(r) * time.Millisecond)
}

func annotate(err error, format string, args ...any) error {
	if err != nil {
		return fmt.Errorf("%s: %w", fmt.Sprintf(format, args...), err)
	}
	return nil
}

func warning(err error, format string, args ...any) {
	if err != nil {
		log.Printf("%s: %s", fmt.Sprintf(format, args...), err)
	}
}
