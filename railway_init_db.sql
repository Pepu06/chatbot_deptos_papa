-- Tablas del chatbot WhatsApp
-- Ejecutar una sola vez en Railway: PostgreSQL service → Console → psql $DATABASE_URL

-- Usuarios de WhatsApp
CREATE TABLE IF NOT EXISTS chatbot_users (
  id         TEXT PRIMARY KEY,   -- número WhatsApp (wa_id)
  name       TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Historial de conversación (ventana de 5 minutos)
CREATE TABLE IF NOT EXISTS chatbot_history (
  id         SERIAL PRIMARY KEY,
  user_id    TEXT REFERENCES chatbot_users(id),
  content    TEXT NOT NULL,
  role       TEXT NOT NULL,
  url_imagen TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chatbot_history_user ON chatbot_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_history_ts   ON chatbot_history(created_at);
