-- A subagent's steps are saved too, under the same thread, in a namespace of their own.
-- Run with: psql -v thread=<thread id>
SELECT count(*) FILTER (WHERE checkpoint_ns = '') AS parent_checkpoints,
       count(*) FILTER (WHERE checkpoint_ns <> '') AS subagent_checkpoints,
       count(DISTINCT checkpoint_ns) FILTER (WHERE checkpoint_ns <> '') AS subagent_namespaces
FROM checkpoints WHERE thread_id = :'thread';
SELECT checkpoint_ns, count(*) AS checkpoints FROM checkpoints
WHERE thread_id = :'thread' AND checkpoint_ns <> '' GROUP BY checkpoint_ns ORDER BY min(checkpoint_id) LIMIT 3;
