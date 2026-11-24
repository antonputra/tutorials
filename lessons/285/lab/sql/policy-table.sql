-- The policy as a vector table, made by langchain-postgres (PGEngine.init_vectorstore_table).
\d policy_sections
SELECT extname, extversion FROM pg_extension ORDER BY extname;
SELECT count(*) AS sections, min(vector_dims(embedding)) AS numbers_in_a_vector FROM policy_sections;
SELECT section, title, length(content) AS characters, left(embedding::text, 60) || '...' AS embedding_starts
FROM policy_sections ORDER BY section LIMIT 3;
-- The search itself, in plain SQL: <=> is pgvector's cosine distance. The sections closest to section 7.
SELECT section, title, round((embedding <=> (SELECT embedding FROM policy_sections WHERE section = 7))::numeric, 4) AS distance
FROM policy_sections ORDER BY embedding <=> (SELECT embedding FROM policy_sections WHERE section = 7) LIMIT 4;
