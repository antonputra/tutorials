-- The agent's long-term memory in Postgres: one row a file. prefix is the namespace, key is the file's path.
SELECT prefix, key, created_at, updated_at, jsonb_pretty(value) AS value FROM store ORDER BY prefix, key;
