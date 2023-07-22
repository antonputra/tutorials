## How do I run a PostgreSQL image?

First of all, you need to run the PostgreSQL Docker container in the background.

```sh
docker run --detach --name my-postgres --env POSTGRES_PASSWORD=devops123 aputra/postgres-169:15.3
```

You don't need to install the PostgreSQL client locally on your laptop. Instead, SSH into the PostgreSQL container by running the following command.

```sh
docker exec -it my-postgres psql -U postgres
```

Verify that you have all the necessary tables.

```sh
\d
```

```
          List of relations
 Schema |   Name   | Type  |  Owner
--------+----------+-------+----------
 public | action   | table | postgres
 public | customer | table | postgres
 public | event    | table | postgres
 public | event_v2 | table | postgres
 public | student  | table | postgres
 public | teacher  | table | postgres
```

## Inner JOIN

```sql
SELECT *
FROM customer
JOIN event
ON customer.customer_id = event.customer_id;
```

## Left JOIN

```sql
SELECT *
FROM customer
LEFT JOIN event
ON customer.customer_id = event.customer_id;
```

## Left Outer JOIN with Exclusion

```sql
SELECT *
FROM customer
LEFT JOIN event
ON customer.customer_id = event.customer_id
WHERE event.customer_id IS NULL;
```

## Right JOIN

```sql
SELECT *
FROM event_v2
RIGHT JOIN action
ON event_v2.action_id = action.action_id;
```

## Rewrite as Left JOIN

```sql
SELECT *
FROM action
LEFT JOIN event_v2
ON action.action_id = event_v2.action_id;
```

## Join 3 tables

```sql
SELECT *
FROM action
LEFT JOIN event_v2
ON event_v2.action_id = action.action_id
LEFT JOIN customer
ON customer.customer_id = event_v2.customer_id;
```

## Select only customer and action names

```sql
SELECT action.name, customer.name
FROM action
LEFT JOIN event_v2
ON event_v2.action_id = action.action_id
LEFT JOIN customer
ON customer.customer_id = event_v2.customer_id;
```

## Full JOIN

```sql
SELECT *
FROM teacher
FULL OUTER JOIN student
ON teacher.age = student.age;
```

## UNION

```sql
SELECT age
FROM teacher
UNION
SELECT age
FROM student;
```

## UNION ALL

```sql
SELECT age
FROM teacher
UNION ALL
SELECT age
FROM student;
```

## CROSS JOIN

```sql
SELECT *
FROM teacher
CROSS JOIN student;
```

## How can I build a multi-architecture Docker image?

```sh

docker build -t aputra/postgres-169-arm64:15.3 --platform linux/arm64 .
docker build -t aputra/postgres-169-amd64:15.3 --platform linux/amd64 .
docker push aputra/postgres-169-arm64:15.3
docker push aputra/postgres-169-amd64:15.3

docker manifest create aputra/postgres-169:15.3 \
    aputra/postgres-169-arm64:15.3 \
    aputra/postgres-169-amd64:15.3

docker manifest push aputra/postgres-169:15.3
```

## How can I manually create tables and insert data?

```sql
CREATE TABLE customer (
  customer_id integer PRIMARY KEY, 
  name varchar(256), 
  address varchar(256)
);

INSERT INTO customer
VALUES 
  (1, 'Casey', '2295 Spring Avenue'), 
  (2, 'Peter', '924 Emma Street'), 
  (3, 'Erika', '397 Terry Lane');

CREATE TABLE event (
  event_id integer PRIMARY KEY, 
  customer_id integer REFERENCES customer(customer_id), 
  action varchar(256)
);

INSERT INTO event
VALUES 
  (101, '3', 'LOGIN'),
  (102, '3', 'VIEW PAGE'),
  (103, '1', 'LOGIN'),
  (104, '1', 'SEARCH');

CREATE TABLE action (
  action_id integer PRIMARY KEY, 
  name varchar(256)
);

INSERT INTO action
VALUES 
  (201, 'LOGIN'),
  (202, 'VIEW PAGE'),
  (203, 'SEARCH'),
  (204, 'LOGOUT');

CREATE TABLE event_v2 (
  event_id integer PRIMARY KEY, 
  customer_id integer REFERENCES customer(customer_id), 
  action_id integer REFERENCES action(action_id)
);

INSERT INTO event_v2
VALUES 
  (101, 2, 201),
  (102, 2, 204);

CREATE TABLE teacher (
  teacher_id integer PRIMARY KEY, 
  name varchar(256), 
  age integer
);

INSERT INTO teacher
VALUES 
  (1, 'Tiffany', 28),
  (2, 'Mathew', 35);


CREATE TABLE student (
  student_id integer PRIMARY KEY, 
  name varchar(256), 
  age integer
);

INSERT INTO student
VALUES 
  (1, 'Ben', 28),
  (2, 'Jenny', 21);
```

## Select all the data

```sql
SELECT * FROM customer;
SELECT * FROM event;
SELECT * FROM action;
SELECT * FROM event_v2;
SELECT * FROM teacher;
SELECT * FROM student;
```