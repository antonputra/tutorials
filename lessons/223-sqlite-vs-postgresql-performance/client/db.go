package main

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	_ "github.com/jackc/pgx/v5/stdlib"
	_ "github.com/mattn/go-sqlite3"
)

func dbConnect(cfg Config) *sql.DB {
	var url string
	if cfg.Test.Db == "pgx" {
		url = fmt.Sprintf("postgres://%s:%s@%s:5432/%s", cfg.Postgres.User, cfg.Postgres.Password, cfg.Postgres.Host, cfg.Postgres.Database)
	} else {
		url = fmt.Sprintf("%s?_journal=%s&_sync=%s&_foreign_keys=%d", cfg.Sqlite.Database, cfg.Sqlite.Journal, cfg.Sqlite.Sync, cfg.Sqlite.ForeignKeys)
	}

	db, err := sql.Open(cfg.Test.Db, url)
	if err != nil {
		log.Fatalf("Unable to connect to database: %s", err)
	}

	db.SetConnMaxLifetime(time.Minute * 1)
	db.SetMaxOpenConns(cfg.Postgres.MaxConnections)
	db.SetMaxIdleConns(cfg.Postgres.MaxConnections)

	return db
}
