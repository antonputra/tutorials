package main

import (
	"fmt"
	"log/slog"
	"math/rand"
	"os"
	"slices"
	"time"
)

// random generates a random number within a specified range.
func random(min int, max int) int {
	return rand.Intn(max-min) + min
}

// sleep pauses the execution of the program.
// Interval is generated randomly with the upper bound limit provided by you.
func sleep(n int) {
	// Generate a random number where the upper bound is n.
	r := rand.Intn(n)

	// Suspend the program's execution.
	time.Sleep(time.Duration(r) * time.Millisecond)
}

// annotate provides an additional context for the error.
func annotate(err error, format string, args ...any) error {
	if err != nil {
		return fmt.Errorf("%s: %w", fmt.Sprintf(format, args...), err)
	}
	return nil
}

// A warn notifies you that something has gone wrong with the execution of the program.
func warn(err error, format string, args ...any) {
	if err != nil {
		slog.Warn(fmt.Sprintf("%s: %s", fmt.Sprintf(format, args...), err))
	}
}

// A fail prints the error message and then exits the program.
func fail(err error, format string, args ...any) {
	if err != nil {
		slog.Error(fmt.Sprintf("%s: %s", fmt.Sprintf(format, args...), err))
		os.Exit(1)
	}
}

// Source for the string generator.
var letterRunes = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

// genString generates a random string with length n
func genString(n int) string {
	// Create a rune slice with length n.
	b := make([]rune, n)

	// Iterate over the rune slice to generate a random string.
	for i := range b {
		b[i] = letterRunes[rand.Intn(len(letterRunes))]
	}

	// Convert the runes to a string and return it.
	return string(b)
}

func validFlag(db string) {
	dbs := []string{"pg", "pg-jsonb", "mg"}
	if !slices.Contains(dbs, db) {
		slog.Error("database is not supported", "db", db, "options", dbs)
		os.Exit(1)
	}
}
