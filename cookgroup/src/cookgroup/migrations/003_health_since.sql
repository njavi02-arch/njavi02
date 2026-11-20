-- "Desde cuándo funciona" y ciclos acumulados por fuente (ESTADO.bat).
ALTER TABLE source_health ADD COLUMN first_ok TEXT;
ALTER TABLE source_health ADD COLUMN ok_cycles INTEGER NOT NULL DEFAULT 0;
