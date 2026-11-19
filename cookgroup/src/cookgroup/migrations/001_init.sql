CREATE TABLE IF NOT EXISTS snapshots (
  store TEXT NOT NULL, product_key TEXT NOT NULL, data TEXT NOT NULL, updated_at TEXT NOT NULL,
  PRIMARY KEY (store, product_key));
CREATE TABLE IF NOT EXISTS alerts (
  dedupe_key TEXT PRIMARY KEY, event_type TEXT NOT NULL, store TEXT NOT NULL,
  product_key TEXT NOT NULL, sent_at TEXT NOT NULL, message_id TEXT);
CREATE TABLE IF NOT EXISTS price_history (
  product_key TEXT NOT NULL, ts TEXT NOT NULL, min_price_cents INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS monitor_runs (
  monitor TEXT NOT NULL, ts TEXT NOT NULL, ok INTEGER NOT NULL, products INTEGER, events INTEGER, error TEXT);
CREATE INDEX IF NOT EXISTS idx_ph ON price_history(product_key, ts);
