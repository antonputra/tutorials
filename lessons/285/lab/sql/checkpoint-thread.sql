-- What one conversation (one thread_id) left in LangGraph's tables. Run with: psql -v thread=<thread id>
SELECT 'checkpoints' AS table_name, count(*) AS rows,
       sum(pg_column_size(checkpoint) + pg_column_size(metadata)) AS bytes FROM checkpoints WHERE thread_id = :'thread'
UNION ALL SELECT 'checkpoint_writes', count(*), sum(octet_length(blob)) FROM checkpoint_writes WHERE thread_id = :'thread'
UNION ALL SELECT 'checkpoint_blobs', count(*), sum(octet_length(blob)) FROM checkpoint_blobs WHERE thread_id = :'thread';
-- The checkpoints, oldest first: one per step of the graph.
SELECT checkpoint_id, checkpoint_ns AS ns, metadata->>'step' AS step, metadata->>'source' AS source,
       checkpoint->>'updated_channels' AS updated_channels
FROM checkpoints WHERE thread_id = :'thread' ORDER BY checkpoint_id;
-- The writes: what each node produced, by channel.
SELECT channel, type, count(*) AS rows, sum(octet_length(blob)) AS bytes
FROM checkpoint_writes WHERE thread_id = :'thread' GROUP BY channel, type ORDER BY rows DESC, channel;
-- The blobs: values too large or too complex to sit inside the checkpoint row.
SELECT channel, type, count(*) AS rows, sum(octet_length(blob)) AS bytes
FROM checkpoint_blobs WHERE thread_id = :'thread' GROUP BY channel, type ORDER BY rows DESC, channel;
