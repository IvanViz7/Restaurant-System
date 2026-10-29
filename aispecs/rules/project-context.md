---
description: "Contexto factual y comandos del proyecto Restaurante. Consulta antes de trabajar en backend, frontend, base de datos o despliegue local."
alwaysApply: true
---

# Contexto del proyecto Restaurante

## Entrada y fuentes de información

- Antes de cualquier tarea, lee `aispecs/AGENTS.md`; contiene las instrucciones de entrada y organización del repositorio.
- Usa este archivo como resumen factual, no como sustituto de las reglas detalladas ni del código actual.
- Reglas generales: [base.md](./base.md). Reglas por área: [backend](./backend-standards.md), [datos](./database-standards.md), [frontend](./frontend-standards.md) y [procesos](./sync-pipeline-standards.md).
- La documentación funcional disponible está bajo `Documentacion/`. No renombres esa carpeta ni asumas que existe `Documentación/`.

## Resumen

Sistema de gestión para restaurantes con soporte multi-organización y multi-sucursal.

| Área | Tecnología actual |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2, psycopg 3 |
| Frontend | React 18, JavaScript, Vite 5, Lucide React |
| Base de datos | PostgreSQL 16 |
| Proxy y TLS | Caddy |
| Contenedores | Docker Compose |
| Autenticación | bcrypt y JWT HS256 |

## Estructura principal

```text
backend/app/       API, autenticación, modelos, conexión y migraciones
frontend/src/      Aplicación React, llamadas API y estilos
frontend/public/   Archivos estáticos y service worker
db/init.sh         Creación inicial del rol PostgreSQL de aplicación
proxy/Caddyfile    Enrutamiento de API y frontend mediante Caddy
aispecs/rules/     Reglas generales y estándares por área
Documentacion/     Documentación funcional disponible en esta copia
respaldos/         Archivos SQL generados localmente; no versionar
```

## Arquitectura y comportamiento confirmado

- El servicio PostgreSQL se llama `db`; la base es `restaurante`. El usuario `admin` es de administración; el backend se conecta con el rol `app`.
- Los secretos se entregan por variables de entorno definidas localmente; no copiar sus valores en documentación o código.
- Las tablas operativas se aíslan por organización con PostgreSQL RLS y el contexto transaccional `app.org_id`. `usuarios` queda fuera de RLS para permitir el login previo a conocer la organización.
- Los roles existentes son `dueno`, `gerente`, `mesero`, `cocinero` y `cajero`. Los controles efectivos de autorización están en el backend.
- Los pedidos conservan precio y costo históricos por línea. El consumo de recetas se registra para mantener la consistencia del inventario al modificar pedidos autorizados.
- Los cambios de esquema se versionan en `backend/app/migraciones.py`; la aplicación aplica las migraciones al iniciar.
- No existe actualmente un pipeline de sincronización de datos externo. Compose sí incluye migraciones al arranque y un servicio de respaldos diarios.

## Puertos y direcciones locales

| Servicio | Dirección desde el host | Puerto interno / notas |
|---|---|---|
| PostgreSQL | `127.0.0.1:5432` | Contenedor `db`, puerto 5432 |
| Vista previa de app | `http://localhost:5600` | Caddy en loopback, puerto interno 8080 |
| Caddy HTTP | `http://localhost:80` | El dominio se configura con `DOMINIO` |
| Caddy HTTPS | `https://localhost:443` | Certificado local de Caddy |
| Backend | No publicado directamente por Compose | Uvicorn dentro del contenedor, puerto 8000 |
| Frontend | No publicado directamente por Compose | Nginx dentro del contenedor, puerto 80 |

En desarrollo frontend, Vite usa `http://localhost:5173` por defecto y reenvía `/api` al backend local `http://localhost:8000`; dentro del entorno Compose, se usa Caddy como proxy.

## Rutas útiles

- API: prefijo `/api`.
- Documentación interactiva: `/api/docs`.
- OpenAPI: `/api/openapi.json`.
- Salud: `/api/salud`.
- WebSocket de cocina: `/api/ws/cocina`.
- La interfaz llama al backend con rutas relativas como `/api/pedidos`, centralizadas en `frontend/src/api.js`.

## Comandos frecuentes

Desde la raíz del repositorio:

```bash
# Levantar los servicios, construyendo imágenes
docker compose up -d --build

# Ver estado y logs
docker compose ps
docker compose logs -f backend

# Reconstruir servicios de aplicación
docker compose build backend frontend

# Abrir PostgreSQL
docker compose exec db psql -U admin -d restaurante

# Probar salud a través del proxy local
curl http://localhost:5600/api/salud

# Build del frontend
cd frontend && npm ci && npm run build
```

El perfil opcional `ia` solo levanta Ollama: `docker compose --profile ia up -d`. No es un proceso de sincronización de datos.

## Validación disponible

`frontend/package.json` declara `npm run build`; actualmente no se observa un runner de pruebas frontend ni una suite automatizada de backend en el repositorio. Antes de afirmar que existe una suite, comprueba los manifiestos vigentes. Valida cambios de API y datos con el flujo afectado, incluyendo permisos, aislamiento y transacciones.
