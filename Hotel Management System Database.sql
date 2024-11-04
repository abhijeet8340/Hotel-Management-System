create database hotel;
use hotel;
CREATE TABLE guests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(15),
    gender VARCHAR(10),
    email VARCHAR(100),
    days INT,
    room_number INT,
    total_cost INT
);
SELECT * FROM guests;

CREATE TABLE checked_out_guests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(15),
    gender VARCHAR(10),
    email VARCHAR(100),
    days INT,
    room_number INT,
    total_cost INT,
    checkout_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM hotel.guests;