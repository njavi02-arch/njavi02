-- Bandeja de salida: un aviso detectado se guarda aquí ANTES de actualizar la instantánea y solo pasa a
-- `alerts` cuando Discord confirma el mensaje. Si Discord falla, se reintenta en el siguiente ciclo (sin pérdida)
-- y la clave única impide duplicados (tras reinicios incluidos).
CREATE TABLE IF NOT EXISTS outbox (
  dedupe_key TEXT PRIMARY KEY, event_type TEXT NOT NULL, store TEXT NOT NULL, product_key TEXT NOT NULL,
  channel TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT, last_attempt_at TEXT);
CREATE TABLE IF NOT EXISTS probe_results (
  source TEXT NOT NULL, domain TEXT, checked_at TEXT NOT NULL, status TEXT NOT NULL, items_read INTEGER,
  items_valid INTEGER, sample TEXT, error TEXT, PRIMARY KEY (source, checked_at));
