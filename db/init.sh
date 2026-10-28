#!/bin/sh
# Rol sin privilegios de superusuario: necesario para que Row Level Security sí se aplique.
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<SQL
CREATE ROLE app LOGIN PASSWORD '$APP_DB_PASSWORD';
GRANT ALL ON SCHEMA public TO app;
SQL
