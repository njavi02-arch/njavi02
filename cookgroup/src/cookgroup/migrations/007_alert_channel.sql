-- v1.0: canal de cada entrega (para «qué canal ha dejado de recibir datos» en el panel)
ALTER TABLE alerts ADD COLUMN channel TEXT;
