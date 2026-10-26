-- 01-store.sql: the online store's orders for the database indexes lab, generated on the container's first start.
-- 10,000,000 orders from 5,000,000 customers over three years, 81 orders on each 8 kB page (123,457 pages), the same rows on
-- every machine (only the dates follow today). Customer 418207 has two orders; account 90311 has 20,000.
-- The same generator measured the video's numbers (research/measure/gen.sql).
\set N 10000000
\set seed 8008
\set pin 1
\set biz 1
\set fk 1
\set logged 1
\set pk 1
\set vacuum 1
\set batch 10000000
SELECT to_char(current_date, 'YYYY-MM-DD') AS today \gset
\echo 'Generating 10,000,000 orders (about 30 seconds on a fast laptop, a few minutes on a slower one)...'
SET timezone = 'UTC';

SELECT :N::bigint * 99 / 100                                   AS nh,       -- history orders; the last 1 % is the sale day
       0.0003 * :N                                              AS n0,       -- orders a day on launch day
       (1.98 * :N / 1096 - 0.0006 * :N) / 1096                  AS b,        -- daily growth of that rate
       extract(epoch FROM (:'today'::date)::timestamp AT TIME ZONE 'UTC')::bigint AS t0,
       3905098::bigint * :N / 10000000                          AS o1,
       8717281::bigint * :N / 10000000                          AS o2,
       180622::bigint * :N / 10000000                           AS bizfrom   -- 90311 signs up before this order
\gset

-- A uniform number in [0, 1) for order i and purpose k: 1 customer, 2 business pick, 3 currency units, 4 cents,
-- 5 cancelled/returned, 6 packing delay, 7 shipping window. hashint8extended is stable across runs and releases.
CREATE FUNCTION u(i bigint, k int) RETURNS float8 LANGUAGE sql IMMUTABLE PARALLEL SAFE
  RETURN (hashint8extended(i, :seed * 16 + k) & 9007199254740991)::float8 / 9007199254740992;

-- Seconds since the epoch at which order i is placed: 1,096 days of history whose daily rate grows linearly
-- (3,000 -> about 15,066 at 10 M), then the sale day, one order every 0.756 s from 00:00 to 21:00 UTC.
CREATE FUNCTION tsec(i bigint) RETURNS float8 LANGUAGE sql IMMUTABLE PARALLEL SAFE RETURN CASE
  WHEN i <= :nh THEN (:t0 - 1096 * 86400)::float8
       + (sqrt((:n0)::float8 ^ 2 + 2 * (:b)::float8 * (i - 0.5)) - (:n0)::float8) / (:b)::float8 * 86400
  ELSE :t0::float8 + (i - :nh - 0.5)::float8 * 75600 / (:N - :nh) END;

CREATE TABLE gen_params AS
SELECT :N::bigint AS n, :seed::int AS seed, (:'today')::date AS today, :nh::bigint AS nh,
       :t0::float8 + 21 * 3600 AS story_now, :o1::bigint AS o1, :o2::bigint AS o2,
       :pin::int::boolean AS pin, :biz::int::boolean AS biz, :batch::bigint AS batch;

\if :fk
CREATE TABLE customers (id bigint NOT NULL, kind text NOT NULL, created_at timestamptz NOT NULL);
-- Customer c signs up an hour before order 2c, so every order's customer already exists.
INSERT INTO customers
SELECT c, CASE WHEN c = 90311 OR c <= 25 THEN 'business' ELSE 'person' END, to_timestamp(tsec(2 * c) - 3600)
FROM generate_series(1, :N::bigint / 2) c;
ALTER TABLE customers ADD PRIMARY KEY (id);
\endif

-- Account 90311's 20,000 orders: the later ids with the smallest hash, an exact count with random gaps.
CREATE TABLE biz (id bigint PRIMARY KEY);
\if :biz
INSERT INTO biz
SELECT i FROM generate_series(:bizfrom + 1, :N::bigint) i
WHERE i NOT IN (:o1, :o2) ORDER BY u(i, 2) LIMIT 20000;
\endif

\if :logged
CREATE TABLE orders (
  id bigint NOT NULL, customer_id bigint NOT NULL, status text NOT NULL,
  total numeric(12,2) NOT NULL, payment_ref text NOT NULL, created_at timestamptz NOT NULL);
\else
CREATE UNLOGGED TABLE orders (
  id bigint NOT NULL, customer_id bigint NOT NULL, status text NOT NULL,
  total numeric(12,2) NOT NULL, payment_ref text NOT NULL, created_at timestamptz NOT NULL);
\endif

-- One session, ascending ids, one INSERT per batch: the table fills page after page, so ctid order = id order =
-- time order (no COPY or CREATE TABLE AS: their bulk extension can leave empty pages at the end).
DO $$
DECLARE
  p gen_params%ROWTYPE;
  lo bigint;
  hi bigint;
BEGIN
  SELECT * INTO p FROM gen_params;
  FOR k IN 0 .. (p.n - 1) / p.batch LOOP
    lo := k * p.batch + 1;
    hi := least(lo + p.batch - 1, p.n);
    INSERT INTO orders (id, customer_id, status, total, payment_ref, created_at)
    SELECT i, c,
      CASE WHEN p.pin AND i IN (p.o1, p.o2) THEN 'delivered'
           WHEN i > p.nh THEN CASE WHEN age_s < (30 + 66 * u(i, 6)) * 60 THEN 'paid' ELSE 'packed' END
           WHEN age_s < (2 + 4 * u(i, 7)) * 86400 THEN 'shipped'
           WHEN u(i, 5) < 0.04 THEN 'cancelled'
           WHEN u(i, 5) < 0.08 THEN 'returned'
           ELSE 'delivered' END,
      -- whole units 5-1,999 (90311: 200-9,999) and cents 01-99, never .00: always a 7-byte numeric
      ((100 * floor(CASE WHEN p.biz AND c = 90311 THEN 200 * 50 ^ u(i, 3) ELSE 5 * 400 ^ u(i, 3) END)::bigint
        + 1 + floor(99 * u(i, 4))::bigint)::numeric / 100),
      'ref_' || left(md5(i::text || ':' || p.seed::text), 24),
      to_timestamp(s)
    FROM generate_series(lo, hi) i
    CROSS JOIN LATERAL (SELECT tsec(i) AS s) t
    CROSS JOIN LATERAL (SELECT p.story_now - t.s AS age_s) a
    CROSS JOIN LATERAL (
      SELECT CASE WHEN p.pin AND i IN (p.o1, p.o2) THEN 418207
                  WHEN p.biz AND i IN (SELECT id FROM biz) THEN 90311
                  ELSE c0 + (c0 IN (90311, 418207))::int END AS c
      -- an earlier-signed-up customer, older customers more often
      FROM (SELECT 1 + floor(((i + 1) / 2) * u(i, 1) ^ 2)::bigint AS c0) z) k;
    COMMIT;
    RAISE NOTICE 'orders: % of %', hi, p.n;
  END LOOP;
END $$;

\if :pk
ALTER TABLE orders ADD PRIMARY KEY (id);
\endif
\if :fk
ALTER TABLE orders ADD FOREIGN KEY (customer_id) REFERENCES customers;
VACUUM (FREEZE, ANALYZE) customers;
\endif
\if :vacuum
VACUUM (FREEZE, ANALYZE) orders;
\else
ANALYZE orders;
\endif
CHECKPOINT;
\echo 'Done: the store is ready.'
