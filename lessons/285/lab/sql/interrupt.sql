-- A paused run in Postgres: the waiting question is a pending write on the __interrupt__ channel.
-- Run with: psql -v thread=<thread id>
SELECT checkpoint_id, task_id, idx, channel, type, octet_length(blob) AS bytes
FROM checkpoint_writes WHERE thread_id = :'thread' AND channel = '__interrupt__';
-- The same blob with its unreadable bytes shown as dots: the tool call that waits for a person.
SELECT regexp_replace(encode(blob, 'escape'), '\\\d{3}', '.', 'g') AS interrupt_blob
FROM checkpoint_writes WHERE thread_id = :'thread' AND channel = '__interrupt__';
SELECT count(*) AS checkpoints, max((metadata->>'step')::int) AS last_step FROM checkpoints WHERE thread_id = :'thread';
