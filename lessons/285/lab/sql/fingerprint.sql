-- One fingerprint for everything the seed wrote about invoices: the same seed must give the same value.
SELECT count(*) AS invoices, max(invoice_number) AS last,
       min(array_length(regexp_split_to_array(trim(document_text), '\s+'), 1)) AS fewest_words,
       max(array_length(regexp_split_to_array(trim(document_text), '\s+'), 1)) AS most_words,
       md5(string_agg(invoice_number::text || total_usd::text || document_text, '' ORDER BY invoice_number)) AS fingerprint
FROM invoices;
