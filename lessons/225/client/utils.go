package main

import (
	"fmt"
	"log"
	"time"

	"golang.org/x/exp/rand"
)

func annotate(err error, format string, args ...any) error {
	if err != nil {
		return fmt.Errorf("%s: %w", fmt.Sprintf(format, args...), err)
	}
	return nil
}

func sleep(us int) {
	r := rand.Intn(us)
	time.Sleep(time.Duration(r) * time.Millisecond)
}

func warning(err error, format string, args ...any) {
	if err != nil {
		log.Printf("%s: %s", fmt.Sprintf(format, args...), err)
	}
}

func fail(err error, format string, args ...any) {
	if err != nil {
		log.Fatalf("%s: %s", fmt.Sprintf(format, args...), err)
	}
}

var letterRunes = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

func getString(n int) string {
	b := make([]rune, n)
	for i := range b {
		b[i] = letterRunes[rand.Intn(len(letterRunes))]
	}
	return string(b)
}
