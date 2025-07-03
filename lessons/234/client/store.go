package main

import (
	"context"
	"log/slog"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
)

type Customer struct {
	Id        int
	Username  string
	FirstName string
	LastName  string
	Address   string
}

type Product struct {
	Id            int
	Name          string
	Price         float32
	StockQuantity int
}

type Cart struct {
	Id         int
	CustomerId int
	Total      float32
}

type CartItem struct {
	Id        int
	CartId    int
	ProductId int
	Quantity  int
}

type Order struct {
	Id         int
	CustomerId int
	Total      float32
}

type OrderItem struct {
	Id        int
	OrderId   int
	ProductId int
	Quantity  int
}

func (c *Cart) createCart(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Observe(time.Since(now).Seconds())
			slog.Debug("shopping cart is created", "id", c.Id, "customer_id", c.CustomerId, "total", c.Total)
		}
	}()

	// Execute the query to create a new device record (pgx automatically prepares and caches statements by default).
	sql := `INSERT INTO cart(customer_id, total) VALUES ($1, $2) RETURNING id`

	err = db.QueryRow(ctx, sql, c.CustomerId, c.Total).Scan(&c.Id)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
	}

	return util.Annotate(err, "db.Exec failed")
}

func (ci *CartItem) addCartItem(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Observe(time.Since(now).Seconds())
			slog.Debug("item added to cart", "id", ci.Id, "cart_id", ci.CartId, "product_id", ci.ProductId, "quantity", ci.Quantity)
		}
	}()

	// Execute the query to create a new device record (pgx automatically prepares and caches statements by default).
	sql := `INSERT INTO cart_item(cart_id, product_id, quantity) VALUES ($1, $2, $3)`
	_, err = db.Exec(ctx, sql, ci.CartId, ci.ProductId, ci.Quantity)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
	}

	return util.Annotate(err, "stmt.Exec failed")
}

func (c *Cart) updateCartTotal(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "update", "db": "postgres"}).Observe(time.Since(now).Seconds())
			slog.Debug("shopping cart total is updated", "id", c.Id, "customer_id", c.CustomerId, "total", c.Total)
		}
	}()

	sql := `UPDATE cart SET total = $1 WHERE customer_id = $2`
	_, err = db.Exec(ctx, sql, c.Total, c.CustomerId)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "update", "db": "postgres"}).Add(1)
	}

	return util.Annotate(err, "stmt.Exec failed")
}

func (o *Order) createOrder(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Observe(time.Since(now).Seconds())
			slog.Debug("order is created", "id", o.Id, "customer_id", o.CustomerId, "total", o.Total)
		}
	}()

	sql := `INSERT INTO "order"(customer_id, total) VALUES ($1, $2) RETURNING id`
	err = db.QueryRow(ctx, sql, o.CustomerId, o.Total).Scan(&o.Id)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
	}

	return util.Annotate(err, "stmt.QueryRow failed")
}

func (oi *OrderItem) addOrderItem(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Observe(time.Since(now).Seconds())
			slog.Debug("item added to order", "id", oi.Id, "cart_id", oi.OrderId, "product_id", oi.ProductId, "quantity", oi.Quantity)
		}
	}()

	sql := `INSERT INTO order_item(order_id, product_id, quantity) VALUES ($1, $2, $3)`
	_, err = db.Exec(ctx, sql, oi.OrderId, oi.ProductId, oi.Quantity)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "insert", "db": "postgres"}).Add(1)
	}

	return util.Annotate(err, "stmt.Exec failed")
}

func (p *Product) updateProductQuantity(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "update", "db": "postgres"}).Observe(time.Since(now).Seconds())
			slog.Debug("product quantity updated", "id", p.Id, "name", p.Name, "price", p.Price, "quantity", p.StockQuantity)
		}
	}()

	sql := `UPDATE product SET stock_quantity = $1 WHERE id = $2`
	_, err = db.Exec(ctx, sql, p.StockQuantity, p.Id)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "update", "db": "postgres"}).Add(1)
	}

	return util.Annotate(err, "stmt.Exec failed")
}

func (ci *CartItem) deleteCartItem(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "delete", "db": "postgres"}).Observe(time.Since(now).Seconds())
			slog.Debug("cart item is deleted", "id", ci.Id, "cart_id", ci.CartId, "product_id", ci.ProductId, "quantity", ci.Quantity)
		}
	}()

	sql := `DELETE FROM cart_item WHERE cart_id = $1`
	_, err = db.Exec(ctx, sql, ci.CartId)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "delete", "db": "postgres"}).Add(1)
	}

	return util.Annotate(err, "stmt.Exec failed")
}

func (o *Order) get(ctx context.Context, db *pgxpool.Pool, m *mon.Metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.Duration.With(prometheus.Labels{"op": "select", "db": "postgres"}).Observe(time.Since(now).Seconds())
			slog.Debug("order", "id", o.Id, "customer_id", o.CustomerId, "total", o.Total)
		}
	}()

	sql := `SELECT id, customer_id, total FROM "order" WHERE id = $1`
	err = db.QueryRow(ctx, sql, o.Id).Scan(&o.Id, &o.CustomerId, &o.Total)
	if err != nil {
		m.Errors.With(prometheus.Labels{"op": "select", "db": "postgres"}).Add(1)
	}

	return util.Annotate(err, "stmt.QueryRow failed")
}
