-- One checkpoint row, whole: the newest one of the thread. Run with: psql -v thread=<thread id>
\x on
SELECT thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type,
       jsonb_pretty(metadata) AS metadata, jsonb_pretty(checkpoint) AS checkpoint
FROM checkpoints WHERE thread_id = :'thread' ORDER BY checkpoint_id DESC LIMIT 1;
