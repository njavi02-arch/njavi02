-- Estado de lanzamientos (calendarios de tiendas) y de stock por talla de fichas vigiladas.
CREATE TABLE IF NOT EXISTS launches (
  uid TEXT PRIMARY KEY,          -- tienda|región|sku
  store TEXT NOT NULL,
  data TEXT NOT NULL,            -- JSON: último Launch visto + estado de tallas
  present INTEGER NOT NULL,      -- 1 si aparecía en el último listado leído correctamente
  first_seen TEXT NOT NULL,
  updated_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_launch_store ON launches(store);
CREATE TABLE IF NOT EXISTS source_health (
  source TEXT PRIMARY KEY, last_ok TEXT, last_error TEXT, last_error_at TEXT, consecutive_errors INTEGER NOT NULL DEFAULT 0,
  last_items INTEGER, last_duration_ms INTEGER, last_delay_s INTEGER);
