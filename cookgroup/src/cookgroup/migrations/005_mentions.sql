-- v0.8: una mención por miembro y señal (aunque el aviso salga en el canal de la tienda y en el agregado)
CREATE TABLE IF NOT EXISTS mentions (
    member_id TEXT NOT NULL,
    signal_key TEXT NOT NULL,
    channel TEXT NOT NULL,
    at TEXT NOT NULL,
    PRIMARY KEY (member_id, signal_key)
);
