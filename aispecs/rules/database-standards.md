---
description: "Estándares de datos para Restaurante: PostgreSQL 16, SQLAlchemy 2, aislamiento RLS, precisión numérica y migraciones."
globs: ["backend/app/modelos.py", "backend/app/migraciones.py", "backend/app/db.py", "db/**", "docker-compose.yml"]
alwaysApply: true
---

# Estándares de base de datos — PostgreSQL 16

## Stack y conexión

- Motor: PostgreSQL 16 (`postgres:16-alpine`) en el servicio `db` de Docker Compose.
- ORM y sesiones: SQLAlchemy 2; driver psycopg 3.
- URL del backend: `DATABASE_URL` con esquema `postgresql+psycopg://`; dentro de Compose, el host es `db:5432` y la base es `restaurante`.
- La aplicación se conecta como el rol sin privilegios `app`. `admin` se reserva para tareas administrativas, inicialización y respaldos.
- `db/init.sh` crea `app` durante la inicialización de un volumen de datos nuevo. No asumas que los scripts de inicialización de PostgreSQL se vuelven a ejecutar en un volumen ya existente.

## Modelos y datos

- Declara los modelos ORM en `backend/app/modelos.py`: clases `PascalCase`, tablas plurales y columnas `snake_case`.
- Conserva las relaciones, restricciones únicas e índices que protegen las reglas del dominio.
- El esquema actual incluye organizaciones, sucursales, usuarios, insumos, existencias, platillos, recetas, mesas, pedidos, líneas de pedido y snapshots de consumo de insumos.
- Las tablas operativas mantienen `organizacion_id`; existencias, mesas y pedidos además se limitan por `sucursal_id` según el flujo.
- `usuarios` no usa RLS porque se consulta durante el login, antes de establecer el contexto de organización. El login debe limitarse por `codigo_restaurante`.
- Usa `Decimal` en Python y `Numeric` para dinero y cantidades persistidas (`Dinero`, `Costo`, `Cantidad`). No conviertas dinero a `float` para almacenarlo.
- Los pedidos guardan precio y costo unitarios al momento de la venta. No derives históricos usando valores actuales del menú o de insumos.

## Aislamiento por organización (RLS)

`backend/app/main.py` activa RLS y `FORCE ROW LEVEL SECURITY` para:

`sucursales`, `insumos`, `existencias`, `platillos`, `receta_items`, `mesas`, `pedidos`, `pedido_items` y `pedido_item_insumos`.

- La política compara `organizacion_id` con `current_setting('app.org_id', true)`.
- En rutas autenticadas, la dependencia de sesión establece ese contexto con `set_config(..., true)` dentro de la transacción.
- Mantén el contexto y usa el rol `app`, que no es superusuario ni propietario con bypass de RLS. No resuelvas errores desactivando RLS o elevando privilegios.
- Incluye filtros explícitos por organización y sucursal cuando el dominio lo requiera; RLS es una defensa adicional, no reemplaza la autorización de la API.

## Consultas y transacciones

- Usa SQLAlchemy 2 (`select`, `Session.scalar`, `Session.scalars`, `Session.execute`) y valores enlazados.
- Para SQL textual usa `text()` con parámetros; no interpolar datos externos en sentencias SQL.
- Usa la dependencia de sesión de la API para establecer RLS, confirmar al finalizar, hacer rollback ante error y cerrar la sesión.
- Agrupa en una transacción los cambios relacionados. En particular, los cambios de pedidos e inventario deben confirmarse o revertirse juntos.
- Usa restricciones de base de datos para invariantes persistentes cuando corresponda, además de validar entradas en el backend.

## Migraciones

- Agrega cada cambio de esquema como una nueva versión en `backend/app/migraciones.py`.
- Las migraciones se ejecutan en una transacción, bajo el bloqueo asesor existente (`31001`), y registran la versión en `schema_migrations`.
- Haz los cambios compatibles con los datos existentes y seguros ante reintentos cuando sea posible; prueba también el arranque contra una base ya poblada.
- No modifiques ni elimines versiones ya aplicadas.
- `Base.metadata.create_all(engine)` crea tablas faltantes, pero no actualiza tablas existentes y no sustituye una migración.

## Respaldos y puertos

- El servicio `respaldos` ejecuta `pg_dump` diario del contenedor `db`, guarda archivos comprimidos en `./respaldos` y elimina los de más de 14 días. Un respaldo no es replicación ni sincronización de datos.
- No sobrescribas, borres ni publiques archivos de respaldo como parte de una tarea rutinaria.
- En desarrollo, PostgreSQL se publica solo en loopback como `127.0.0.1:5432`; no cambies ese alcance sin una necesidad explícita y revisión de seguridad.
- Para abrir una consola desde la raíz del proyecto: `docker compose exec db psql -U admin -d restaurante`.

## Validación de cambios de datos

Verifica la migración en una base con datos existentes, el aislamiento entre organizaciones, las restricciones afectadas y la coherencia de transacciones. Si agregas pruebas automatizadas de base de datos, documenta cómo ejecutarlas y ejecútalas.
