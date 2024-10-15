package main

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	_ "github.com/go-sql-driver/mysql"
	_ "github.com/jackc/pgx/v5/stdlib"
)

func dbConnect(cfg Config) *sql.DB {
	var url string
	if cfg.Test.Db == "pgx" {
		url = fmt.Sprintf("postgres://%s:%s@%s:5432/%s", cfg.Db.User, cfg.Db.Password, cfg.Db.Host, cfg.Db.Database)
	} else {
		url = fmt.Sprintf("%s:%s@tcp(%s:3306)/%s", cfg.Db.User, cfg.Db.Password, cfg.Db.Host, cfg.Db.Database)
	}

	db, err := sql.Open(cfg.Test.Db, url)
	if err != nil {
		log.Fatalf("Unable to connect to database: %s", err)
	}

	db.SetConnMaxLifetime(time.Minute * 1)
	db.SetMaxOpenConns(cfg.Db.MaxConnections)
	db.SetMaxIdleConns(cfg.Db.MaxConnections)

	return db
}
