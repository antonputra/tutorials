package main

import (
	"context"
	"fmt"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type mongodb struct {
	// MonfoDB instance.
	db *mongo.Database

	// Application configuration object.
	config *Config

	// Context for the program
	context context.Context
}

// Initializes NewMongo and establishes connections with database.
func NewMongo(ctx context.Context, c *Config) *mongodb {
	mg := mongodb{
		config:  c,
		context: ctx,
	}
	mg.mgConnect(ctx)

	return &mg
}

// dbConnect creates a connection pool to connect to MongoDB.
func (mg *mongodb) mgConnect(ctx context.Context) {
	uri := fmt.Sprintf("mongodb://%s:27017", mg.config.Mongo.Host)

	opts := options.Client().SetMaxPoolSize(mg.config.Mongo.MaxConnections)

	// Connect to the MongoDB database.
	client, err := mongo.Connect(ctx, opts.ApplyURI(uri))
	fail(err, "Unable to create connection pool")

	mg.db = client.Database(mg.config.Mongo.Database)
}
