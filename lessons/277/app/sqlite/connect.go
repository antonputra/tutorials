// Package sqlite provides utilities to connect to the SQLite database.
package sqlite

import (
	"app/config"
	"database/sql"
	"fmt"

	"github.com/antonputra/go-utils/util"
)

// Connect establishes connection with the SQLite database.
func Connect(cfg *config.Config) *sql.DB {
	uri := fmt.Sprintf("%s?_journal=%s&_sync=%s&_foreign_keys=%d",
		cfg.Sqlite.Database, cfg.Sqlite.Journal, cfg.Sqlite.Sync, cfg.Sqlite.ForeignKeys)

	db, err := sql.Open("sqlite3", uri)
	util.Fail(err, "failed to connect to sqlite, uri: %s", uri)

	return db
}
