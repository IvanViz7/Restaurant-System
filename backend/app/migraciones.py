from sqlalchemy import text

from .db import engine


def aplicar_migraciones():
    with engine.begin() as conexion:
        conexion.execute(text("SELECT pg_advisory_xact_lock(31001)"))
        conexion.execute(text(
            "CREATE TABLE IF NOT EXISTS schema_migrations "
            "(version VARCHAR(64) PRIMARY KEY, aplicada_en TIMESTAMPTZ NOT NULL DEFAULT now())"
        ))
        version = "0001_codigo_restaurante"
        aplicada = conexion.scalar(
            text("SELECT 1 FROM schema_migrations WHERE version = :version"), {"version": version}
        )
        if not aplicada:
            conexion.execute(text("ALTER TABLE organizaciones ADD COLUMN IF NOT EXISTS codigo VARCHAR(40)"))
            conexion.execute(text(
                "UPDATE organizaciones SET codigo = 'rest-' || lpad(id::text, 6, '0') WHERE codigo IS NULL"
            ))
            conexion.execute(text("ALTER TABLE organizaciones ALTER COLUMN codigo SET NOT NULL"))
            conexion.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_organizaciones_codigo ON organizaciones (codigo)"
            ))
            conexion.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:version)"), {"version": version}
            )

        version = "0002_consumo_pedido_items"
        aplicada = conexion.scalar(
            text("SELECT 1 FROM schema_migrations WHERE version = :version"), {"version": version}
        )
        if not aplicada:
            conexion.execute(text(
                "ALTER TABLE pedido_items ADD COLUMN IF NOT EXISTS consumo_registrado "
                "BOOLEAN NOT NULL DEFAULT false"
            ))
            conexion.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:version)"), {"version": version}
            )

        version = "0003_usuario_empleados"
        aplicada = conexion.scalar(
            text("SELECT 1 FROM schema_migrations WHERE version = :version"), {"version": version}
        )
        if not aplicada:
            conexion.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS usuario VARCHAR(32)"))
            conexion.execute(text(
                "UPDATE usuarios SET usuario = 'usuario-' || id::text WHERE usuario IS NULL"
            ))
            conexion.execute(text("ALTER TABLE usuarios ALTER COLUMN email DROP NOT NULL"))
            conexion.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_organizacion_usuario "
                "ON usuarios (organizacion_id, lower(usuario)) WHERE usuario IS NOT NULL"
            ))
            conexion.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:version)"), {"version": version}
            )