-- Create Tables
CREATE TABLE facebook (
  name VARCHAR(50), 
  friends INT
);

CREATE TABLE linkedin (
  name VARCHAR(50), 
  connections INT
);

-- Populate Tables
INSERT INTO facebook(name, friends) 
VALUES 
  ('Liam', 380), 
  ('Olivia', 90), 
  ('James', 450), 
  ('Noah', 6);

INSERT INTO linkedin(name, connections) 
VALUES 
  ('Sophia', 500), 
  ('Noah', 124), 
  ('Olivia', 20), 
  ('Liam', 890);

-- LEFT JOIN
SELECT *
FROM facebook
LEFT JOIN linkedin
ON facebook.name = linkedin.name;
