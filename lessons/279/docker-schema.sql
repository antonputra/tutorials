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

-- Create the Sizes table
CREATE TABLE sizes (
    size VARCHAR(10) PRIMARY KEY
);

-- Create the Colors table
CREATE TABLE colors (
    color TEXT PRIMARY KEY
);

INSERT INTO sizes (size)
VALUES 
  ('Small'), ('Medium'), ('Large');

INSERT INTO colors (color) 
VALUES 
  ('Black'), ('Red');
