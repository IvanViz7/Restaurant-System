# Guía del proyecto

## Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2 y psycopg 3.
- **Frontend:** React 18, Vite 5 y JavaScript; se sirve con Nginx. Lucide React provee iconos.
- **Base de datos:** PostgreSQL 16.
- **Proxy:** Caddy termina HTTPS y enruta la API y el frontend.
- **Desarrollo y despliegue local:** Docker Compose.

## Estructura

- `backend/app/`: API, autenticación, seguridad, modelos SQLAlchemy, conexión a PostgreSQL y migraciones.
- `backend/requirements.txt`: dependencias Python.
- `frontend/src/`: aplicación React, llamadas a API y estilos.
- `frontend/public/`: recursos estáticos de la PWA.
- `frontend/package.json` y `frontend/package-lock.json`: dependencias y lockfile; instalar con `npm ci`.
- `db/init.sh`: inicialización del rol de aplicación PostgreSQL.
- `proxy/Caddyfile`: rutas HTTP/HTTPS hacia API y frontend.
- `Documentacion/`: documentación que existe actualmente en esta copia del repositorio.
- `Documentación/`: ruta canónica indicada para la documentación. Aún no coincide con el nombre actual `Documentacion/`; no crear una copia duplicada ni renombrar la existente sin actualizar sus enlaces.
- `aispecs/commands/` y `aispecs/rules/`: ubicaciones previstas para comandos y reglas de IA.
- `respaldos/`: respaldos SQL generados localmente; no versionar su contenido.
- `.github/instructions/` y `.github/prompts/`: personalizaciones de GitHub Copilot del repositorio.

## Decisiones arquitectónicas

- **Multi-tenant:** las entidades operativas incluyen `organizacion_id`; PostgreSQL aplica Row Level Security. El backend se conecta con el rol de aplicación `app`, no como superusuario.
- **Multi-sucursal:** los recursos operativos se limitan a una sucursal. Dueño y gerente pueden operar entre sucursales; los roles operativos usan la sucursal de su sesión.
- **Autenticación:** el acceso requiere código único del restaurante y usuario/contraseña. Empleados usan username sin correo; el dueño puede usar username o correo. Usernames no distinguen mayúsculas y son únicos dentro de cada restaurante.
- **Roles:** la autorización se verifica en el backend además de filtrar la navegación del frontend. Dueño y gerente comparten permisos; cocinero consulta en modo lectura; cajero consulta y cobra; mesero gestiona pedidos dentro de las reglas de preparación y cobro.
- **Migraciones:** los cambios de esquema van en versiones nuevas de `backend/app/migraciones.py`. `Base.metadata.create_all()` crea objetos faltantes, pero no sustituye migraciones para tablas existentes.
- **Pedidos e inventario:** cada línea conserva precio y costo históricos. Los snapshots de consumo permiten restaurar inventario al editar o eliminar pedidos autorizados.
- **Proxy local:** `https://localhost` usa Caddy con certificado local; `http://localhost:5600` es una vista previa HTTP limitada a loopback.
- **Secretos:** `.env` y credenciales locales no se versionan. No escribir valores secretos en documentación, logs o pruebas.

## Comandos habituales

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f backend
docker compose build backend frontend
docker compose exec db psql -U admin -d restaurante
```

La documentación interactiva de FastAPI está en `/api/docs`. No se encontró una suite automatizada persistente; al añadir una, probar permisos por rol, aislamiento de organización/sucursal y migraciones sobre PostgreSQL.

## Cambios futuros

- Mantener las reglas de autorización en el servidor; ocultar botones no es una medida de seguridad.
- Añadir una migración versionada al cambiar modelos o restricciones de PostgreSQL.
- Actualizar la documentación funcional y los planes cuando cambien contratos, roles o flujos.
- No eliminar ni sobrescribir datos de usuario, respaldos o archivos locales como parte de tareas rutinarias.