-- Script para verificar y corregir el esquema de Supabase
-- Ejecuta esto en el SQL Editor de Supabase

-- 1. Verificar si la tabla users existe y su estructura
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- 2. Si la tabla no existe o le falta la columna phone, ejecuta esto:

-- Crear tabla users (id es el número de teléfono de WhatsApp)
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,  -- WhatsApp phone number (wa_id)
  name TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Verificar/crear tabla history
CREATE TABLE IF NOT EXISTS history (
  id SERIAL PRIMARY KEY,
  user_id TEXT REFERENCES users(id),
  content TEXT NOT NULL,
  role TEXT NOT NULL, -- 'user' o 'assistant'
  url_imagen TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Verificar/crear tabla departamentos
CREATE TABLE IF NOT EXISTS departamentos (
  id SERIAL PRIMARY KEY,
  address TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Verificar/crear tabla mensajes
CREATE TABLE IF NOT EXISTS mensajes (
  id SERIAL PRIMARY KEY,
  departamento_id INTEGER REFERENCES departamentos(id),
  content TEXT NOT NULL,
  url_imagen TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 6. Crear índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id);
CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at);
CREATE INDEX IF NOT EXISTS idx_departamentos_address ON departamentos(address);

-- 7. Verificar que todo está bien
SELECT 'users' as table_name, COUNT(*) as column_count 
FROM information_schema.columns 
WHERE table_name = 'users'
UNION ALL
SELECT 'history', COUNT(*) 
FROM information_schema.columns 
WHERE table_name = 'history'
UNION ALL
SELECT 'departamentos', COUNT(*) 
FROM information_schema.columns 
WHERE table_name = 'departamentos'
UNION ALL
SELECT 'mensajes', COUNT(*) 
FROM information_schema.columns 
WHERE table_name = 'mensajes';
