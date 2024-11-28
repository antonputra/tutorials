# MongoDB vs. PostgreSQL: Performance & Functionality

You can find tutorial [here](https://youtu.be/ZZ2tx8iL3P4).

## SQL

```sql
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    jdoc jsonb
);

CREATE INDEX idx__product__price ON product using BTREE(((jdoc -> 'price')::NUMERIC));

INSERT INTO product(jdoc) VALUES ('{"name": "Shampoo", "price": 7.90, "stock": 100}');
INSERT INTO product(jdoc) VALUES ('{"name": "Hairspray", "price": 11.50, "stock": 100}');

UPDATE product SET jdoc = jsonb_set(jdoc, '{stock}', '98') WHERE id = 2;
SELECT id, jdoc->'price' as price, jdoc->'stock' as stock FROM product WHERE (jdoc -> 'price')::numeric < 10;
DELETE FROM product WHERE id = 1;

CREATE VIEW sales AS
  SELECT "order".product_id, "order".quantity, inventory.price
  FROM "order"
  LEFT OUTER JOIN inventory ON "order".product_id = inventory.product_id;

SELECT product_id, SUM(quantity * price) AS amount_sold FROM sales GROUP BY product_id;
```

```json
db.product.insertOne({name: "Shampoo", price: 7.90, stock: 100})
db.product.insertOne({name: "Hairspray", price: 11.50, stock: 100})

db.product.updateOne({ _id: ObjectId("674705957b0ee5f68236d2b1") }, { $set: { 'stock': 98 } })
db.product.find({ price: { $lt: 10 } })
db.product.deleteOne( {"_id": ObjectId("674705957b0ee5f68236d2b1")})

db.createView( "sales", "order", [
   {
      $lookup:
         {
            from: "inventory",
            localField: "product_id",
            foreignField: "product_id",
            as: "inventory_docs"
         }
   },
   {
      $project:
         {
           _id: 0,
           product_id: 1,
           quantity: 1,
           price: "$inventory_docs.price"
         }
   },
      { $unwind: "$price" }
] );

db.sales.aggregate( [
   {
      $group:
         {
            _id: "$product_id",
            amount_sold: { $sum: { $multiply: [ "$price", "$quantity" ] } }
         }
   }
] );
```
