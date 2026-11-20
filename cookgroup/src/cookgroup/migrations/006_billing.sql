-- v0.9: membresías de pago (Stripe) y acceso por rol en Discord
CREATE TABLE IF NOT EXISTS members (
    discord_id TEXT PRIMARY KEY, username TEXT, stripe_customer TEXT, linked_at TEXT
);
CREATE TABLE IF NOT EXISTS subscriptions (
    id TEXT PRIMARY KEY, discord_id TEXT NOT NULL, plan TEXT, status TEXT NOT NULL, current_period_end INTEGER,
    cancel_at_period_end INTEGER DEFAULT 0, livemode INTEGER DEFAULT 0, started_at TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY, discord_id TEXT, amount_cents INTEGER, currency TEXT, status TEXT, kind TEXT,
    livemode INTEGER DEFAULT 0, at TEXT
);
CREATE TABLE IF NOT EXISTS stripe_events (
    id TEXT PRIMARY KEY, type TEXT, livemode INTEGER, received_at TEXT, result TEXT
);
CREATE TABLE IF NOT EXISTS role_sync (
    discord_id TEXT PRIMARY KEY, desired INTEGER, actual INTEGER, status TEXT, attempts INTEGER DEFAULT 0,
    last_error TEXT, last_sync_at TEXT, welcomed INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS audit (
    at TEXT, actor TEXT, action TEXT, target TEXT, detail TEXT
);
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT, discord_id TEXT, subject TEXT, status TEXT, opened_at TEXT, closed_at TEXT
);
