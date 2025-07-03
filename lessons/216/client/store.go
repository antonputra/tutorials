package main

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

type Customer struct {
	Id        int64
	Username  string
	FirstName string
	LastName  string
	Address   string
}

type Product struct {
	Id            int64
	Name          string
	Price         float32
	StockQuantity int64
}

type Cart struct {
	Id         int64
	CustomerId int64
	Total      float32
}

type CartItem struct {
	Id        int64
	CartId    int64
	ProductId int64
	Quantity  int64
}

type Order struct {
	Id         int64
	CustomerId int64
	Total      float32
}

type OrderItem struct {
	Id        int64
	OrderId   int64
	ProductId int64
	Quantity  int64
}

func prepStmt(db *sql.DB, c Config, op string) (stmt *sql.Stmt, err error) {
	if c.Test.Db == "pgx" && op == "create_cart" {
		return db.Prepare("INSERT INTO cart(customer_id, total) VALUES ($1, $2) RETURNING id")
	} else if c.Test.Db == "mysql" && op == "create_cart" {
		return db.Prepare("INSERT INTO cart(customer_id, total) VALUES (?, ?)")
	} else if c.Test.Db == "pgx" && op == "add_cart_item" {
		return db.Prepare("INSERT INTO cart_item(cart_id, product_id, quantity) VALUES ($1, $2, $3)")
	} else if c.Test.Db == "mysql" && op == "add_cart_item" {
		return db.Prepare("INSERT INTO cart_item(cart_id, product_id, quantity) VALUES (?, ?, ?)")
	} else if c.Test.Db == "pgx" && op == "update_cart_total" {
		return db.Prepare("UPDATE cart SET total = $1 WHERE customer_id = $2")
	} else if c.Test.Db == "mysql" && op == "update_cart_total" {
		return db.Prepare("UPDATE cart SET total = ? WHERE customer_id = ?")
	} else if c.Test.Db == "pgx" && op == "create_order" {
		return db.Prepare(`INSERT INTO "order"(customer_id, total) VALUES ($1, $2) RETURNING id`)
	} else if c.Test.Db == "mysql" && op == "create_order" {
		return db.Prepare("INSERT INTO `order`(customer_id, total) VALUES (?, ?)")
	} else if c.Test.Db == "pgx" && op == "add_order_item" {
		return db.Prepare("INSERT INTO order_item(order_id, product_id, quantity) VALUES ($1, $2, $3)")
	} else if c.Test.Db == "mysql" && op == "add_order_item" {
		return db.Prepare("INSERT INTO order_item(order_id, product_id, quantity) VALUES (?, ?, ?)")
	} else if c.Test.Db == "pgx" && op == "update_product_quantity" {
		return db.Prepare("UPDATE product SET stock_quantity = $1 WHERE id = $2")
	} else if c.Test.Db == "mysql" && op == "update_product_quantity" {
		return db.Prepare("UPDATE product SET stock_quantity = ? WHERE id = ?")
	} else if c.Test.Db == "pgx" && op == "delete_cart_item" {
		return db.Prepare("DELETE FROM cart_item WHERE cart_id = $1")
	} else if c.Test.Db == "mysql" && op == "delete_cart_item" {
		return db.Prepare("DELETE FROM cart_item WHERE cart_id = ?")
	} else if c.Test.Db == "pgx" && op == "delete_cart" {
		return db.Prepare("DELETE FROM cart WHERE id = $1")
	} else if c.Test.Db == "mysql" && op == "delete_cart" {
		return db.Prepare("DELETE FROM cart WHERE id = ?")
	} else if c.Test.Db == "pgx" && op == "test2" {
		return db.Prepare(`SELECT customer.username, customer.first_name, customer.last_name, customer.address, product.name, order_item.quantity, "order".total FROM "order" LEFT JOIN customer ON customer.id = "order".customer_id LEFT JOIN order_item ON order_item.order_id = "order".id LEFT JOIN product ON product.id = order_item.product_id WHERE "order".id = $1`)
	} else if c.Test.Db == "mysql" && op == "test2" {
		return db.Prepare("SELECT customer.username, customer.first_name, customer.last_name, customer.address, product.name, order_item.quantity, `order`.total FROM `order` LEFT JOIN customer ON customer.id = `order`.customer_id LEFT JOIN order_item ON order_item.order_id = `order`.id LEFT JOIN product ON product.id = order_item.product_id WHERE `order`.id = ?")
	} else {
		return nil, fmt.Errorf("Operation: %s NOT supported", op)
	}
}

func (c *Cart) createCart(stmt *sql.Stmt, cfg Config, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "insert", "method": "create_cart"}).Observe(time.Since(now).Seconds())
		}
	}()

	if cfg.Test.Db == "pgx" {
		err = stmt.QueryRow(c.CustomerId, c.Total).Scan(&c.Id)
		return annotate(err, "stmt.QueryRow failed")
	} else {
		res, err := stmt.Exec(c.CustomerId, c.Total)
		if err != nil {
			return annotate(err, "stmt.Exec failed")
		}
		c.Id, err = res.LastInsertId()
		return annotate(err, "res.LastInsertId failed")
	}
}

func (ci *CartItem) addCartItem(stmt *sql.Stmt, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "insert", "method": "add_cart_item"}).Observe(time.Since(now).Seconds())
		}
	}()

	_, err = stmt.Exec(ci.CartId, ci.ProductId, ci.Quantity)
	return annotate(err, "stmt.Exec failed")
}

func (c *Cart) updateCartTotal(stmt *sql.Stmt, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "update", "method": "update_cart_total"}).Observe(time.Since(now).Seconds())
		}
	}()

	_, err = stmt.Exec(c.Total, c.CustomerId)
	return annotate(err, "stmt.Exec failed")
}

func (o *Order) createOrder(stmt *sql.Stmt, cfg Config, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "insert", "method": "create_order"}).Observe(time.Since(now).Seconds())
		}
	}()

	if cfg.Test.Db == "pgx" {
		err = stmt.QueryRow(o.CustomerId, o.Total).Scan(&o.Id)
		return annotate(err, "stmt.QueryRow failed")
	} else {
		res, err := stmt.Exec(o.CustomerId, o.Total)
		if err != nil {
			return annotate(err, "stmt.Exec failed")
		}
		o.Id, err = res.LastInsertId()
		return annotate(err, "res.LastInsertId failed")
	}
}

func (oi *OrderItem) addOrderItem(stmt *sql.Stmt, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "insert", "method": "add_order_item"}).Observe(time.Since(now).Seconds())
		}
	}()

	_, err = stmt.Exec(oi.OrderId, oi.ProductId, oi.Quantity)
	return annotate(err, "stmt.Exec failed")
}

func (p *Product) updateProductQuantity(stmt *sql.Stmt, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "update", "method": "update_product_quantity"}).Observe(time.Since(now).Seconds())
		}
	}()

	_, err = stmt.Exec(p.StockQuantity, p.Id)
	return annotate(err, "stmt.Exec failed")
}

func (ci *CartItem) deleteCartItem(stmt *sql.Stmt, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "delete", "method": "delete_cart_item"}).Observe(time.Since(now).Seconds())
		}
	}()

	_, err = stmt.Exec(ci.CartId)
	return annotate(err, "stmt.Exec failed")
}

func (c *Cart) deleteCart(stmt *sql.Stmt, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "delete", "method": "delete_cart"}).Observe(time.Since(now).Seconds())
		}
	}()

	_, err = stmt.Exec(c.Id)
	return annotate(err, "stmt.Exec failed")
}

func (o *Order) selectOrder(stmt *sql.Stmt, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "read", "method": "select_order"}).Observe(time.Since(now).Seconds())
		}
	}()

	_, err = stmt.Exec(o.Id)
	return annotate(err, "stmt.Exec failed")
}
