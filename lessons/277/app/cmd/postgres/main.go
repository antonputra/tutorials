package main

import (
	"app/config"
	"app/models"
	"app/postgres"
	"context"
	"fmt"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/prometheus/client_golang/prometheus"
)

func main() {
	cfg := config.Load()

	ctx, done := context.WithCancel(context.Background())
	defer done()

	// Create Prometheus metrics.
	histLabels := []string{"op", "method"}

	reg := prometheus.NewRegistry()
	m := mon.NewMetrics("postgres", []string{}, []string{}, histLabels, reg)
	mon.StartPrometheus(cfg.MetricsPort, reg)

	db := postgres.Connect(ctx, cfg)

	// Run the database migration to create tables, indexes, and populate them with sample data.
	migrate(ctx, db, cfg)

	// Run the main test.
	test(ctx, cfg, db, m)
}

func test(ctx context.Context, cfg *config.Config, db *pgxpool.Pool, m *mon.Metrics) {
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
			cart := models.Cart{CustomerId: customer.Id, Total: 0.0}
			err := cart.InsertCartPGX(ctx, db, m)
			util.Fail(err, "fail to insert cart")

			// Add product to the shopping cart
			cartItem := models.CartItem{CartId: cart.Id, ProductId: product.Id, Quantity: int64(util.Random(1, 10))}
			err = cartItem.InsertCartItemPGX(ctx, db, m)
			util.Fail(err, "fail to insert cart item")

			// Update value of the shopping cart
			cart.Total = product.Price * float64(cartItem.Quantity)
			err = cart.UpdateCartPGX(ctx, db, m)
			util.Fail(err, "fail to update cart")

			// Create an order
			order := models.Order{CustomerId: cart.CustomerId, Total: cart.Total}
			err = order.InsertOrderPGX(ctx, db, m)
			util.Fail(err, "fail to create order")

			// Add product to the order
			orderItem := models.OrderItem{OrderId: order.Id, ProductId: cartItem.ProductId, Quantity: cartItem.Quantity}
			err = orderItem.InsertOrderItemPGX(ctx, db, m)
			util.Fail(err, "fail to insert order")

			// Reduce the stock quantity of the product (set to random value)
			product.StockQuantity = int64(util.Random(0, 100))
			err = product.UpdateProductPGX(ctx, db, m)
			util.Fail(err, "fail to update product")

			// Delete shopping cart items
			err = cartItem.DeleteCartItemPGX(ctx, db, m)
			util.Fail(err, "fail to delete cart item")

			// Delete shopping cart
			err = cart.DeleteCartPGX(ctx, db, m)
			util.Fail(err, "fail to delete cart")

			// Create order report
			orderReport := models.OrderReport{OrderId: order.Id}
			orderReport.SelectOrderPGX(ctx, db, m)

			if delay > 0 {
				time.Sleep(time.Duration(delay) * time.Microsecond)
			}
		}
	}
}
