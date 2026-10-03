-- E-commerce starter schema (PostgreSQL)
-- Goals: NL2SQL-friendly names, strong FK integrity, simple joins, queryable timestamps.

CREATE TABLE IF NOT EXISTS customers (
  customer_id      BIGSERIAL PRIMARY KEY,
  full_name        TEXT NOT NULL,
  email            TEXT UNIQUE NOT NULL,
  city             TEXT NOT NULL,
  country          TEXT NOT NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categories (
  category_id      BIGSERIAL PRIMARY KEY,
  category_name    TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
  product_id       BIGSERIAL PRIMARY KEY,
  product_name     TEXT NOT NULL,
  category_id      BIGINT NOT NULL REFERENCES categories(category_id),
  price            NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
  order_id         BIGSERIAL PRIMARY KEY,
  customer_id      BIGINT NOT NULL REFERENCES customers(customer_id),
  order_date       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status           TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','paid','shipped','cancelled','refunded')),
  total_amount     NUMERIC(12,2) NOT NULL CHECK (total_amount >= 0)
);

-- NOTE: The schema does not enforce a minimum of one order_item per order.
-- Standard SQL constraints cannot express "child table must have at least one row."
-- Intent: every order must have at least one item (enforced in the service layer
-- at order creation time). If stricter DB-level enforcement is needed later,
-- add a DEFERRABLE INITIALLY DEFERRED trigger on order_items (DELETE/UPDATE)
-- and orders (INSERT) that checks COUNT(order_items) > 0 at commit time.
CREATE TABLE IF NOT EXISTS order_items (
  order_item_id    BIGSERIAL PRIMARY KEY,
  order_id         BIGINT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  product_id       BIGINT NOT NULL REFERENCES products(product_id),
  quantity         INT NOT NULL CHECK (quantity > 0),
  unit_price       NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
  line_total       NUMERIC(12,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- Helpful indexes for common NL2SQL patterns
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
