# Sistema para restaurantes (MVP)

Python (FastAPI) · React (PWA) · Postgres · Caddy · todo con Docker Compose.

## Arranque
```bash
cp .env.example .env        # cambia las contraseñas y el JWT_SECRET
docker compose up -d --build
```
Abre https://localhost (acepta el certificado local) y pulsa **Registrar mi restaurante**.
API y documentación interactiva: https://localhost/api/docs

## Primeros pasos en la app
1. Al registrar el restaurante, guarda el código único que aparece en la cabecera. Los empleados lo usan con su username y contraseña; el dueño puede usar username (`dueno`) o correo.
2. En **Usuarios**, dueño o gerente puede crear cuentas asignando username, contraseña, rol y sucursal; los empleados no necesitan correo.
3. En **Almacén**, agrega insumos; luego crea platillos y recetas en **Menú** y mesas en **Mesas**.
4. En **Pedidos**, dueño, gerente o mesero crea y gestiona pedidos; solo se editan/eliminan mientras cocina no haya comenzado y antes del cobro.
5. **Cocina** permite al cocinero consultar pedidos en modo lectura. **Cajero** consulta cuentas abiertas y las cobra.
6. **Resumen** muestra ventas, food cost, top y bottom de platillos/bebidas.

Los restaurantes existentes reciben un código `rest-<id>` al aplicar la migración. Las cuentas existentes reciben un username `usuario-<id>` sin cambiar contraseña ni correo. El username generado aparece en **Usuarios**; cambiarlo no está disponible todavía.

## Roles
- **Dueño y gerente:** mismas funciones administrativas, incluida la gestión de usuarios.
- **Mesero:** administra pedidos de su sucursal antes de que cocina empiece y antes de cobrar.
- **Cocinero:** consulta pedidos y no puede modificarlos ni cambiar estados.
- **Cajero:** consulta y cobra cuentas abiertas; no crea ni modifica pedidos.

## Arquitectura
- **Multi-tenant:** cada tabla operativa lleva `organizacion_id` y Postgres aplica Row Level Security (rol `app` sin superusuario, ver `db/init.sh`).
- **Multi-sucursal:** tablas operativas con `sucursal_id`; el dueño elige sucursal con `?sucursal_id=`, el resto queda fijo a la suya.
- **Costos históricos:** cada línea de pedido guarda precio y costo del momento, así los márgenes pasados no cambian si luego sube un insumo.
- **Respaldos:** el contenedor `respaldos` genera un `pg_dump` diario en `./respaldos` (14 días). Copia esa carpeta a un disco externo o la nube.
- **IA local (fase 2):** `docker compose --profile ia up -d` levanta Ollama.
