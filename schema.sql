
-- CUSTOMER
CREATE TABLE Customer (
    customerID SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    firstName VARCHAR(50),
    lastName VARCHAR(50),
    street VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    zipcode VARCHAR(10)
);

-- CREDIT CARD
CREATE TABLE CreditCard (
    cardNum VARCHAR(20) PRIMARY KEY,
    expirationDate DATE NOT NULL,
    customerID INT REFERENCES Customer(customerID) ON DELETE CASCADE
);

-- STAFF
CREATE TABLE Staff (
    staffID SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    firstName VARCHAR(50),
    lastName VARCHAR(50)
);

-- PRODUCT
CREATE TABLE Product (
    productID SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    quantity INT NOT NULL,
    category VARCHAR(50)
);

-- PURCHASE
CREATE TABLE Purchase (
    purchaseID SERIAL PRIMARY KEY,
    cardNum VARCHAR(20) REFERENCES CreditCard(cardNum) ON DELETE SET NULL,
    customerID INT REFERENCES Customer(customerID) ON DELETE CASCADE,
    productID INT REFERENCES Product(productID) ON DELETE SET NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    purchaseDate DATE NOT NULL DEFAULT CURRENT_DATE
);


-- Insert Customers
INSERT INTO Customer (username, password, firstName, lastName, street, city, state, zipcode)
VALUES 
('jsmith', 'pass123', 'John', 'Smith', '123 Maple St', 'Boston', 'MA', '02118'),
('adoe', 'secure456', 'Alice', 'Doe', '456 Oak Ave', 'Cambridge', 'OH', '02139');

-- Insert Credit Cards
INSERT INTO CreditCard (cardNum, expirationDate, customerID)
VALUES 
('1111222233334444', '2026-05-01', 1),
('5555666677778888', '2027-10-15', 2);

-- Insert Staff
INSERT INTO Staff (username, password, role, firstName, lastName)
VALUES 
('mgr_jane', 'admin789', 'Manager', 'Jane', 'Lee'),
('clerk_bob', 'clerk000', 'Clerk', 'Bob', 'Taylor');

-- Insert Products
INSERT INTO Product (name, price, quantity, category)
VALUES 
('Wireless Mouse', 29.99, 100, 'Electronics'),
('USB-C Cable', 9.99, 200, 'Accessories'),
('Water Bottle', 14.50, 150, 'Fitness');

-- Insert Purchases
INSERT INTO Purchase (cardNum, customerID, date)
VALUES 
('1111222233334444', 1, '2025-08-01'),
('5555666677778888', 2, '2025-08-02');

