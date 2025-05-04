package main

import (
	"log"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

func main() {
	cfg := new(Config)
	cfg.loadConfig("config.yaml")

	reg := prometheus.NewRegistry()
	m := NewMetrics(reg)
	StartPrometheusServer(cfg, reg)

	runTest(*cfg, m)
}

func runTest(cfg Config, m *metrics) {
	log.Printf("Running Test: %s-%s", cfg.Test.Db, cfg.Test.Name)
	currentClients := cfg.Test.MinClients

	// Establish connection to the database
	db := dbConnect(cfg)

	// Prepare SQL statements
	createCartStmt, err := prepStmt(db, cfg, "create_cart")
	warning(err, "Unable to prepare create_cart statement")

	addCartItemStmt, err := prepStmt(db, cfg, "add_cart_item")
	warning(err, "Unable to prepare add_cart_item statement")

	updateCartTotalStmt, err := prepStmt(db, cfg, "update_cart_total")
	warning(err, "Unable to prepare update_cart_total statement")

	createOrderStmt, err := prepStmt(db, cfg, "create_order")
	warning(err, "Unable to prepare update_cart_total statement")

	addOrderItemStmt, err := prepStmt(db, cfg, "add_order_item")
	warning(err, "Unable to prepare add_order_item statement")

	updateProductQuantityStmt, err := prepStmt(db, cfg, "update_product_quantity")
	warning(err, "Unable to prepare update_product_quantity statement")

	deleteCartItemStmt, err := prepStmt(db, cfg, "delete_cart_item")
	warning(err, "Unable to prepare delete_cart_item statement")

	selectOrder, err := prepStmt(db, cfg, "test2")
	warning(err, "Unable to prepare select order statement")

	for {
		clients := make(chan struct{}, currentClients)
		m.clients.Set(float64(currentClients))

		now := time.Now()
		for {
			clients <- struct{}{}
			go func() {
				sleep(cfg.Test.RequestDelayMs)

				if cfg.Test.Name == "test1" {
					// Create shopping cart
					cart := Cart{CustomerId: random(1, 10), Total: 0}
					err = cart.createCart(createCartStmt, cfg, m)
					warning(err, "Failed to create shopping cart")

					// Add the first product into the shopping cart
					product1 := Product{Id: random(1, 10), Price: float32(random(1, 100)), StockQuantity: random(1, 200)}
					cartItem := CartItem{CartId: cart.Id, ProductId: product1.Id, Quantity: random(1, 100)}
					err = cartItem.addCartItem(addCartItemStmt, m)
					warning(err, "Failed to add the first product into the shopping cart")

					// Add the second product into the shopping cart
					product2 := Product{Id: random(1, 10), Price: float32(random(1, 100)), StockQuantity: random(1, 200)}
					cartItem2 := CartItem{CartId: cart.Id, ProductId: product2.Id, Quantity: random(1, 100)}
					err = cartItem2.addCartItem(addCartItemStmt, m)
					warning(err, "Failed to add the second product into the shopping cart")

					// Update the shopping cart total
					cart.Total = float32(random(1, 100))
					err = cart.updateCartTotal(updateCartTotalStmt, m)
					warning(err, "Failed to update the shopping cart total")

					// Create an order after the customer has made a payment
					order := Order{CustomerId: cart.CustomerId, Total: cart.Total}
					err = order.createOrder(createOrderStmt, cfg, m)
					warning(err, "Failed to create an order")

					// Add the first product into the order
					orderItem := OrderItem{OrderId: order.Id, ProductId: cartItem.ProductId, Quantity: cartItem.Quantity}
					err = orderItem.addOrderItem(addOrderItemStmt, m)
					warning(err, "Failed to add the first product into the order")

					// Reduce the stock quantity of the first product
					err = product1.updateProductQuantity(updateProductQuantityStmt, m)
					warning(err, "Failed to reduce the stock quantity of the first product")

					// Add the second product into the order
					orderItem2 := OrderItem{OrderId: order.Id, ProductId: cartItem2.ProductId, Quantity: cartItem2.Quantity}
					err = orderItem2.addOrderItem(addOrderItemStmt, m)
					warning(err, "Failed to add the second product into the order")

					// Reduce the stock quantity of the second product
					err = product2.updateProductQuantity(updateProductQuantityStmt, m)
					warning(err, "Failed to reduce the stock quantity of the second product")

					// Remove the first product from the shopping cart
					err = cartItem.deleteCartItem(deleteCartItemStmt, m)
					warning(err, "Failed to remove the first product from the shopping cart")

					// Remove the second product from the shopping cart
					err = cartItem2.deleteCartItem(deleteCartItemStmt, m)
					warning(err, "Failed to remove the second product from the shopping cart")

				} else if cfg.Test.Name == "test2" {
					sleep(cfg.Test.RequestDelayMs)

					// Select an order
					order := Order{Id: random(1, int64(cfg.Test.MaxOrderId))}
					err = order.selectOrder(selectOrder, m)
					warning(err, "Failed to select order")
				} else {
					log.Fatalf("%s test is not supported!", cfg.Test.Name)
				}

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
