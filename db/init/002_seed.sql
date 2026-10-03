-- 002_seed.sql (PostgreSQL) — deterministic seed data (with customers.city)
-- Assumes 001_schema.sql already created tables:
-- customers (with city), categories, products, orders, order_items

BEGIN;

-- ------------------------------------------------------------
-- Categories (IDs will be 1..N deterministically on fresh init)
-- ------------------------------------------------------------
INSERT INTO categories (category_name) VALUES
  ('Electronics'),
  ('Clothing'),
  ('Home'),
  ('Books'),
  ('Sports'),
  ('Beauty');

-- ------------------------------------------------------------
-- Customers (NOW includes city)
-- ------------------------------------------------------------
INSERT INTO customers (full_name, email, city, country, created_at) VALUES
  ('Ava Müller',   'ava.mueller@example.com',   'Berlin',    'Germany',  '2025-10-05T10:15:00+00'),
  ('Noah Schmidt', 'noah.schmidt@example.com',  'Munich',    'Germany',  '2025-10-12T14:20:00+00'),
  ('Mia Rossi',    'mia.rossi@example.com',     'Milan',     'Italy',    '2025-11-02T09:05:00+00'),
  ('Liam Dubois',  'liam.dubois@example.com',   'Paris',     'France',   '2025-11-10T17:45:00+00'),
  ('Emma Novak',   'emma.novak@example.com',    'Vienna',    'Austria',  '2025-11-18T08:30:00+00'),
  ('Olivia Silva', 'olivia.silva@example.com',  'Lisbon',    'Portugal', '2025-12-01T12:00:00+00');

-- ------------------------------------------------------------
-- Products
-- (Category IDs: 1 Electronics, 2 Clothing, 3 Home, 4 Books, 5 Sports, 6 Beauty)
-- ------------------------------------------------------------
INSERT INTO products (product_name, category_id, price, is_active, created_at) VALUES
  ('Wireless Mouse',              1,  24.99, TRUE, '2025-10-01T10:00:00+00'),
  ('Mechanical Keyboard',         1,  89.00, TRUE, '2025-10-01T10:00:00+00'),
  ('USB-C Charger',               1,  19.50, TRUE, '2025-10-02T10:00:00+00'),
  ('Noise Cancelling Headphones', 1, 149.00, TRUE, '2025-10-03T10:00:00+00'),

  ('Cotton T-Shirt',              2,  15.00, TRUE, '2025-10-04T10:00:00+00'),
  ('Denim Jeans',                 2,  49.90, TRUE, '2025-10-05T10:00:00+00'),
  ('Hoodie',                      2,  39.90, TRUE, '2025-10-06T10:00:00+00'),

  ('Coffee Maker',                3,  79.00, TRUE, '2025-10-07T10:00:00+00'),
  ('LED Desk Lamp',               3,  29.99, TRUE, '2025-10-08T10:00:00+00'),
  ('Non-stick Pan',               3,  34.50, TRUE, '2025-10-09T10:00:00+00'),

  ('Intro to SQL',                4,  29.00, TRUE, '2025-10-10T10:00:00+00'),
  ('FastAPI in Practice',         4,  35.00, TRUE, '2025-10-11T10:00:00+00'),

  ('Yoga Mat',                    5,  22.00, TRUE, '2025-10-12T10:00:00+00'),
  ('Running Shoes',               5,  89.99, TRUE, '2025-10-13T10:00:00+00'),
  ('Water Bottle',                5,  12.50, TRUE, '2025-10-14T10:00:00+00'),

  ('Face Moisturizer',            6,  18.90, TRUE, '2025-10-15T10:00:00+00'),
  ('Shampoo',                     6,   9.90, TRUE, '2025-10-16T10:00:00+00'),
  ('Sunscreen SPF50',             6,  14.90, TRUE, '2025-10-17T10:00:00+00');

-- ------------------------------------------------------------
-- Orders
-- Customer IDs: 1..6 (same order as customers insert)
-- Totals match sum(order_items.line_total)
-- ------------------------------------------------------------
INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES
  (1, '2026-01-05T10:00:00+00', 'paid',     63.99),  -- order_id = 1
  (2, '2026-01-06T16:30:00+00', 'shipped',  79.90),  -- order_id = 2
  (3, '2026-01-10T09:20:00+00', 'paid',    178.99),  -- order_id = 3
  (1, '2026-01-12T13:00:00+00', 'paid',     64.00),  -- order_id = 4
  (4, '2026-01-15T18:10:00+00', 'pending', 124.49),  -- order_id = 5
  (5, '2026-01-18T11:45:00+00', 'paid',    148.00),  -- order_id = 6
  (6, '2026-01-20T08:05:00+00', 'paid',     58.60),  -- order_id = 7
  (2, '2026-01-25T20:00:00+00', 'refunded',128.90);  -- order_id = 8

-- ------------------------------------------------------------
-- Order items
-- Product IDs follow insertion order above:
-- 1 Mouse, 2 Keyboard, 3 Charger, 4 Headphones,
-- 5 T-Shirt, 6 Jeans, 7 Hoodie,
-- 8 Coffee Maker, 9 Desk Lamp, 10 Pan,
-- 11 Intro to SQL, 12 FastAPI in Practice,
-- 13 Yoga Mat, 14 Running Shoes, 15 Water Bottle,
-- 16 Moisturizer, 17 Shampoo, 18 Sunscreen SPF50
-- ------------------------------------------------------------

-- Order 1 total: 24.99 + (2*19.50=39.00) = 63.99
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (1, 1, 1, 24.99),
  (1, 3, 2, 19.50);

-- Order 2 total: 49.90 + (2*15.00=30.00) = 79.90
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (2, 6, 1, 49.90),
  (2, 5, 2, 15.00);

-- Order 3 total: 149.00 + 29.99 = 178.99
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (3, 4, 1, 149.00),
  (3, 9, 1, 29.99);

-- Order 4 total: 29.00 + 35.00 = 64.00
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (4, 11, 1, 29.00),
  (4, 12, 1, 35.00);

-- Order 5 total: 89.99 + 12.50 + 22.00 = 124.49
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (5, 14, 1, 89.99),
  (5, 15, 1, 12.50),
  (5, 13, 1, 22.00);

-- Order 6 total: 79.00 + (2*34.50=69.00) = 148.00
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (6, 8,  1, 79.00),
  (6, 10, 2, 34.50);

-- Order 7 total: 18.90 + (2*14.90=29.80) + 9.90 = 58.60
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (7, 16, 1, 18.90),
  (7, 18, 2, 14.90),
  (7, 17, 1,  9.90);

-- Order 8 total: 39.90 + 89.00 = 128.90
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (8, 7, 1, 39.90),
  (8, 2, 1, 89.00);

COMMIT;
