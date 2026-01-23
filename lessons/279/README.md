# 6 SQL Joins you MUST know! (Animated + Practice)

You can find tutorial [here](https://youtu.be/9prkapPewGs).

## To practice SQL, run the following commands:

```bash
docker run --detach --name my-postgres --env POSTGRES_PASSWORD=devops123 aputra/postgres-279:v2
docker exec -it my-postgres psql -U postgres
```

## Inner Join

```sql
SELECT *
FROM facebook
INNER JOIN linkedin
ON facebook.name = linkedin.name;
```

## Left Join

```sql
SELECT *
FROM facebook
LEFT JOIN linkedin
ON facebook.name = linkedin.name;
```

## Right Join

```sql
SELECT *
FROM facebook
RIGHT JOIN linkedin
ON facebook.name = linkedin.name;
```

## Full Outer Join

```sql
SELECT *
FROM facebook
FULL OUTER JOIN linkedin
ON facebook.name = linkedin.name;
```

## Union

```sql
SELECT name, friends
FROM facebook
UNION ALL
SELECT name, connections
FROM linkedin;
```

## Cross

```sql
SELECT sizes.size, colors.color
FROM sizes
CROSS JOIN colors;
```
