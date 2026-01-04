package main

import (
	"app/config"
	"app/models"
	"app/sqlite"
	"context"
	"database/sql"
	"fmt"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	_ "github.com/mattn/go-sqlite3"
	"github.com/prometheus/client_golang/prometheus"
)

func main() {
	cfg := config.Load()

	ctx, done := context.WithCancel(context.Background())
	defer done()

	// Create Prometheus metrics.
	histLabels := []string{"op", "method"}

	reg := prometheus.NewRegistry()
	m := mon.NewMetrics("sqlite", []string{}, []string{}, histLabels, reg)
	mon.StartPrometheus(cfg.MetricsPort, reg)

	db := sqlite.Connect(cfg)

	// Run the database migration to create tables, indexes, and populate them with sample data.
	migrate(ctx, db, cfg)

	// Run the main test.
	test(ctx, cfg, db, m)
}

func test(ctx context.Context, cfg *config.Config, db *sql.DB, m *mon.Metrics) {
	delay := cfg.Test.Delay

	ticker := time.NewTicker(time.Duration(cfg.Test.Interval) * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			if delay > 0 {
				delay -= cfg.Test.Step
				fmt.Printf("The current delay is %d microseconds.\n", delay)
			}

		default:
			// Pick random customer from sample data
			customer := cfg.Customers[util.Random(0, 9)]

			// Pick random product from sample data
			product := cfg.Products[util.Random(0, 9)]

			// Create an empty shopping cart for the selected customer
			stmt := sqlite.InsertCart(db)
			cart := models.Cart{CustomerId: customer.Id, Total: 0.0}
			err := cart.InsertCartSQL(ctx, stmt, m)
			util.Fail(err, "fail to insert cart")

			// Add product to the shopping cart
			stmt = sqlite.InsertCartItem(db)
			cartItem := models.CartItem{CartId: cart.Id, ProductId: product.Id, Quantity: int64(util.Random(1, 10))}
			err = cartItem.InsertCartItemSQL(ctx, stmt, m)
			util.Fail(err, "fail to insert cart item")

			// Update value of the shopping cart
			stmt = sqlite.UpdateCart(db)
			cart.Total = product.Price * float64(cartItem.Quantity)
			err = cart.UpdateCartSQL(ctx, stmt, m)
			util.Fail(err, "fail to update cart")

			// Create an order
			stmt = sqlite.InsertOrder(db)
			order := models.Order{CustomerId: cart.CustomerId, Total: cart.Total}
			err = order.InsertOrderSQL(ctx, stmt, m)
			util.Fail(err, "fail to create order")

			// Add product to the order
			stmt = sqlite.InsertOrderItem(db)
			orderItem := models.OrderItem{OrderId: order.Id, ProductId: cartItem.ProductId, Quantity: cartItem.Quantity}
			err = orderItem.InsertOrderItemSQL(ctx, stmt, m)
			util.Fail(err, "fail to insert order")

			// Reduce the stock quantity of the product (set to random value)
			stmt = sqlite.UpdateProduct(db)
			product.StockQuantity = int64(util.Random(0, 100))
			err = product.UpdateProductSQL(ctx, stmt, m)
			util.Fail(err, "fail to update product")

			// Delete shopping cart items
			stmt = sqlite.DeleteCartItem(db)
			err = cartItem.DeleteCartItemSQL(ctx, stmt, m)
			util.Fail(err, "fail to delete cart item")

			// Delete shopping cart
			stmt = sqlite.DeleteCart(db)
			err = cart.DeleteCartSQL(ctx, stmt, m)
			util.Fail(err, "fail to delete cart")

			// Create order report
			orderReport := models.OrderReport{OrderId: order.Id}
			stmt = sqlite.SelectOrder(db)
			orderReport.SelectOrderSQL(ctx, stmt, m)

			if delay > 0 {
				time.Sleep(time.Duration(delay) * time.Microsecond)
			}
		}
	}
}
