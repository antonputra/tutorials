## Create customer table

CREATE TABLE customer (
  customer_id integer PRIMARY KEY, 
  name varchar(256), 
  address varchar(256)
);

INSERT INTO customer
VALUES 
  (1, 'Casey', '2295 Spring Avenue'), 
  (2, 'Peter', '924 Emma Street'), 
  (3, 'Erika', '397 Terry Lane');



CREATE TABLE event (
  event_id integer PRIMARY KEY, 
  customer_id integer REFERENCES customer(customer_id), 
  action varchar(256)
);

INSERT INTO event
VALUES 
  (101, '3', 'LOGIN'),
  (102, '3', 'VIEW PAGE'),
  (103, '1', 'LOGIN'),
  (104, '1', 'SEARCH');



CREATE TABLE action (
  action_id integer PRIMARY KEY, 
  name varchar(256)
);

INSERT INTO action
VALUES 
  (201, 'LOGIN'),
  (202, 'VIEW PAGE'),
  (203, 'SEARCH'),
  (204, 'LOGOUT');



CREATE TABLE event_v2 (
  event_id integer PRIMARY KEY, 
  customer_id integer REFERENCES customer(customer_id), 
  action_id integer REFERENCES action(action_id)
);

INSERT INTO event_v2
VALUES 
  (101, 2, 201),
  (102, 2, 204);



CREATE TABLE teacher (
  teacher_id integer PRIMARY KEY, 
  name varchar(256), 
  age integer
);

INSERT INTO teacher
VALUES 
  (1, 'Tiffany', 28),
  (2, 'Mathew', 35);



CREATE TABLE student (
  student_id integer PRIMARY KEY, 
  name varchar(256), 
  age integer
);

INSERT INTO student
VALUES 
  (1, 'Ben', 28),
  (2, 'Jenny', 21);

## Check data

SELECT * FROM customer;
SELECT * FROM event;
SELECT * FROM action;
SELECT * FROM event_v2;
SELECT * FROM teacher;
SELECT * FROM student;