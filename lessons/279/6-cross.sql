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

SELECT sizes.size, colors.color
FROM sizes
CROSS JOIN colors;
