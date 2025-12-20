package main

import (
	"context"
	"strconv"
	"time"

	"github.com/antonputra/go-utils/util"
	"github.com/gofiber/fiber/v3"
	"github.com/jackc/pgx/v5/pgxpool"
)

type server struct {
	db  *pgxpool.Pool
	cfg *Config
}

func newServer(ctx context.Context, cfg *Config) *server {
	s := server{cfg: cfg}
	s.db = DbConnect(ctx, cfg)

	return &s
}

func (s *server) getHealth(c fiber.Ctx) error {
	return c.SendStatus(200)
}

func (s *server) getUsers(c fiber.Ctx) error {
	users := []User{
		{
			Id:      1,
			Name:    "David D. Patton",
			Address: "1670 Stiles Street",
			Phone:   "412-578-3857",
			Image:   "user.png",
		},
		{
			Id:      2,
			Name:    "Gary E. Eaton",
			Address: "828 Collins Avenue",
			Phone:   "614-866-1660",
			Image:   "user.png",
		},
		{
			Id:      3,
			Name:    "John J. Fox",
			Address: "1895 Columbia Mine Road",
			Phone:   "304-505-3622",
			Image:   "user.png",
		},
	}

	return c.Status(fiber.StatusOK).JSON(users)
}

func (s *server) saveUser(c fiber.Ctx) error {
	u := new(User)

	if err := c.Bind().Body(u); err != nil {
		return util.Annotate(err, "failed to decode user")
	}

	now := time.Now()
	u.CreatedAt = now
	u.UpdatedAt = now
	u.Image = "user-go-" + strconv.FormatInt(now.UnixMilli(), 10) + ".png"

	sql := `INSERT INTO go_app (name, address, phone, image, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id`
	err := u.Save(c.Context(), s.db, sql)
	if err != nil {
		return util.Annotate(err, "failed to save user")
	}

	return c.Status(fiber.StatusCreated).JSON(u)
}
