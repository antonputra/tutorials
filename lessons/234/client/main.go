package main

import (
	"context"
	"flag"
	"log/slog"
	"time"

	mon "github.com/antonputra/go-utils/monitoring"
	"github.com/antonputra/go-utils/util"
	"github.com/prometheus/client_golang/prometheus"
)

func main() {
	cp := flag.String("config", "", "path to the config")
	flag.Parse()

	ctx, done := context.WithCancel(context.Background())
	defer done()

	cfg := new(Config)
	cfg.LoadConfig(*cp)

	if cfg.Debug {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}

	db := dbConnect(ctx, cfg)

	reg := prometheus.NewRegistry()
	mon.StartPrometheusServer(cfg.MetricsPort, reg)

	m := mon.NewMetrics(reg)

	currentClients := cfg.Test.MinClients

	for {
		clients := make(chan struct{}, currentClients)
		m.Clients.Set(float64(currentClients))

		now := time.Now()
		for {
			clients <- struct{}{}
			go func() {
				// // Create shopping cart
				cart := Cart{CustomerId: util.Random(1, 10), Total: 0}
				err := cart.createCart(ctx, db, m)
				util.Warn(err, "failed to create shopping cart")

				// Add the first product into the shopping cart
				product1 := Product{Id: util.Random(1, 10), Price: float32(util.Random(1, 100)), StockQuantity: util.Random(1, 200)}
				cartItem := CartItem{CartId: cart.Id, ProductId: product1.Id, Quantity: util.Random(1, 100)}
				err = cartItem.addCartItem(ctx, db, m)
				util.Warn(err, "failed to add the first product into the shopping cart")

				// Add the second product into the shopping cart
				product2 := Product{Id: util.Random(1, 10), Price: float32(util.Random(1, 100)), StockQuantity: util.Random(1, 200)}
				cartItem2 := CartItem{CartId: cart.Id, ProductId: product2.Id, Quantity: util.Random(1, 100)}
				err = cartItem2.addCartItem(ctx, db, m)
				util.Warn(err, "failed to add the second product into the shopping cart")

				// Update the shopping cart total
				cart.Total = float32(util.Random(1, 100))
				err = cart.updateCartTotal(ctx, db, m)
				util.Warn(err, "failed to update the shopping cart total")

				// Create an order after the customer has made a payment
				order := Order{CustomerId: cart.CustomerId, Total: cart.Total}
				err = order.createOrder(ctx, db, m)
				util.Warn(err, "failed to create an order")

				// Add the first product into the order
				orderItem := OrderItem{OrderId: order.Id, ProductId: cartItem.ProductId, Quantity: cartItem.Quantity}
				err = orderItem.addOrderItem(ctx, db, m)
				util.Warn(err, "failed to add the first product into the order")

				// Reduce the stock quantity of the first product
				err = product1.updateProductQuantity(ctx, db, m)
				util.Warn(err, "failed to reduce the stock quantity of the first product")

				// Add the second product into the order
				orderItem2 := OrderItem{OrderId: order.Id, ProductId: cartItem2.ProductId, Quantity: cartItem2.Quantity}
				err = orderItem2.addOrderItem(ctx, db, m)
				util.Warn(err, "failed to add the second product into the order")

				// Reduce the stock quantity of the second product
				err = product2.updateProductQuantity(ctx, db, m)
				util.Warn(err, "failed to reduce the stock quantity of the second product")

				// Remove the first product from the shopping cart
				err = cartItem.deleteCartItem(ctx, db, m)
				util.Warn(err, "failed to remove the first product from the shopping cart")

				// Remove the second product from the shopping cart
				err = cartItem2.deleteCartItem(ctx, db, m)
				util.Warn(err, "failed to remove the second product from the shopping cart")

				// Get order by id
				err = order.get(ctx, db, m)
				util.Warn(err, "failed to get order by id")

				util.Sleep(cfg.Test.RequestDelayMs)

				<-clients
			}()

			if time.Since(now).Seconds() >= float64(cfg.Test.StageIntervalS) {
				break
			}
		}

		if currentClients == cfg.Test.MaxClients {
			break
		}
		currentClients += 1
	}
}
