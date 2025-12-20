package main

import (
	"context"
	"time"

	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
)

type User struct {
	Id        int       `json:"id"`
	Name      string    `json:"name"`
	Address   string    `json:"address"`
	Phone     string    `json:"phone"`
	Image     string    `json:"image"`
	CreatedAt time.Time `json:"createdAt,omitzero"`
	UpdatedAt time.Time `json:"updatedAt,omitzero"`
}

func (u *User) Save(ctx context.Context, db *pgxpool.Pool, sql string) (err error) {
	err = db.QueryRow(ctx, sql, u.Name, u.Address, u.Phone, u.Image, u.CreatedAt, u.UpdatedAt).Scan(&u.Id)

	return util.Annotate(err, "db.QueryRow failed")
}
