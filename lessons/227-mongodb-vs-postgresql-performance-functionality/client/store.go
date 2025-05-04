package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type product struct {
	PostgresId  int      `bson:"postgresId,omitempty" json:"postgresId,omitempty"`
	MongoId     string   `bson:"mongoId,omitempty" json:"mongoId,omitempty"`
	Name        string   `bson:"name,omitempty" json:"name,omitempty"`
	Description string   `bson:"description,omitempty" json:"description,omitempty"`
	Price       float32  `bson:"price,omitempty" json:"price,omitempty"`
	Stock       int      `bson:"stock,omitempty" json:"stock,omitempty"`
	Colors      []string `bson:"colors,omitempty" json:"colors,omitempty"`
}

func (p *product) create(pg *postgres, mg *mongodb, db string, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "insert", "method": "create_product"}).Observe(time.Since(now).Seconds())
			slog.Debug("product is created", "postgresId", p.PostgresId, "mongoId", p.MongoId, "name", p.Name)
		}
	}()

	if db == "pg" {
		b, err := json.Marshal(p)
		fail(err, "json.Marshal(p) failed")

		err = pg.dbpool.QueryRow(pg.context, `INSERT INTO product(jdoc) VALUES ($1) RETURNING id`, b).Scan(&p.PostgresId)

		return annotate(err, "pg.dbpool.QueryRow")
	} else {
		res, err := mg.db.Collection("product").InsertOne(mg.context, p)
		p.MongoId = res.InsertedID.(primitive.ObjectID).Hex()

		return annotate(err, "InsertOne failed")
	}
}

func (p *product) update(pg *postgres, mg *mongodb, db string, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "update", "method": "update_inventory"}).Observe(time.Since(now).Seconds())
			slog.Debug("product is updated", "postgresId", p.PostgresId, "mongoId", p.MongoId, "stock", p.Stock)
		}
	}()

	if db == "pg" {
		_, err = pg.dbpool.Exec(pg.context, `UPDATE product SET jdoc = jsonb_set(jdoc, '{stock}', $1) WHERE id = $2`, p.Stock, p.PostgresId)

		return annotate(err, "pg.dbpool.QueryRow")

	} else {
		id, _ := primitive.ObjectIDFromHex(p.MongoId)
		filter := bson.D{{Key: "_id", Value: id}}
		update := bson.D{{Key: "$set", Value: bson.D{{Key: "stock", Value: p.Stock}}}}

		_, err := mg.db.Collection("product").UpdateOne(mg.context, filter, update)

		return annotate(err, "UpdateOne failed")
	}
}

func (p *product) search(pg *postgres, mg *mongodb, db string, m *metrics, debug bool) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "select", "method": "select_inventory"}).Observe(time.Since(now).Seconds())
		}
	}()

	if db == "pg" {
		rows, err := pg.dbpool.Query(pg.context, `SELECT id, jdoc->'price' as price, jdoc->'stock' as stock FROM product WHERE (jdoc -> 'price')::numeric < $1 LIMIT 5`, 30)
		defer rows.Close()

		if debug {
			for rows.Next() {
				lp := product{}
				err := rows.Scan(&lp.PostgresId, &lp.Price, &lp.Stock)
				fail(err, "unable to scan row")
				slog.Debug("low priced products", "id", lp.PostgresId, "price", lp.Price, "stock", lp.Stock)
			}
		}

		return annotate(err, "pg.dbpool.Query")
	} else {
		filter := bson.D{{Key: "price", Value: bson.D{{Key: "$lt", Value: 30}}}}

		opts := options.Find().SetLimit(5)
		cursor, err := mg.db.Collection("product").Find(mg.context, filter, opts)

		if debug {
			var results []product
			if err = cursor.All(context.TODO(), &results); err != nil {
				panic(err)
			}
			for _, result := range results {
				res, _ := bson.MarshalExtJSON(result, false, false)
				fmt.Println(string(res))
			}
		}

		return annotate(err, "Read failed")
	}
}

func (p *product) delete(pg *postgres, mg *mongodb, db string, m *metrics) (err error) {
	now := time.Now()
	defer func() {
		if err == nil {
			m.duration.With(prometheus.Labels{"operation": "delete", "method": "delete_cart"}).Observe(time.Since(now).Seconds())
			slog.Debug("product is deleted", "postgresId", p.PostgresId, "mongoId", p.MongoId, "name", p.Name)
		}
	}()

	if db == "pg" {
		_, err = pg.dbpool.Exec(pg.context, `DELETE FROM product WHERE id = $1`, p.PostgresId)

		return annotate(err, "pg.dbpool.QueryRow")
	} else {
		id, _ := primitive.ObjectIDFromHex(p.MongoId)
		filter := bson.D{{Key: "_id", Value: id}}

		_, err := mg.db.Collection("product").DeleteOne(mg.context, filter)

		return annotate(err, "DeleteOne failed")
	}
}
