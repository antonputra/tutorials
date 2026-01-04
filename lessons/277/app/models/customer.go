package models

import (
	"context"
	"database/sql"

	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Customer struct {
	Id        int64  `yaml:"id"`
	Username  string `yaml:"username"`
	FirstName string `yaml:"first_name"`
	LastName  string `yaml:"last_name"`
	Address   string `yaml:"address"`
}

func (c *Customer) InsertCustomerSQL(ctx context.Context, stmt *sql.Stmt) (err error) {
	err = stmt.QueryRowContext(ctx, c.Id, c.Username, c.FirstName, c.LastName, c.Address).Scan(&c.Id)

	return util.Annotate(err, "InsertCustomerSQL failed")
}

func (c *Customer) InsertCustomerPGX(ctx context.Context, db *pgxpool.Pool) (err error) {
	// PostgreSQL driver automatically prepares and caches statements.
	sql := `
	INSERT INTO customer(id, username, first_name, last_name, address)
	VALUES ($1, $2, $3, $4, $5) RETURNING id;`

	err = db.QueryRow(ctx, sql, c.Id, c.Username, c.FirstName, c.LastName, c.Address).Scan(&c.Id)

	return util.Annotate(err, "InsertCustomerPGX failed")
}
