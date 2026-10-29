---
description: "Estándares del backend Restaurante: FastAPI, Python 3.12, validación, autorización, SQLAlchemy y API."
globs: ["backend/**/*.py", "backend/requirements.txt", "backend/Dockerfile"]
alwaysApply: true
---

# Estándares de backend — FastAPI

## Stack y organización

| Componente | Tecnología | Ubicación |
|---|---|---|
| Runtime | Python 3.12 | `backend/Dockerfile` |
| API | FastAPI y Uvicorn | `backend/app/main.py` |
| Validación de entrada | Pydantic | Esquemas de `backend/app/main.py` |
| ORM y sesiones | SQLAlchemy 2 | `backend/app/db.py`, `backend/app/modelos.py` |
| Driver PostgreSQL | psycopg 3 | `backend/requirements.txt` |
| Autenticación | bcrypt y PyJWT HS256 | `backend/app/seguridad.py` |

Conserva la estructura actual. Mantén nombres de dominio en español, módulos y funciones en `snake_case`, clases en `PascalCase` y constantes en `UPPER_SNAKE_CASE`.

## Rutas, contratos y errores

- Implementa rutas REST bajo el router `/api` en `backend/app/main.py`. Los endpoints vigentes incluyen `/api/docs`, `/api/openapi.json`, `/api/salud` y el WebSocket `/api/ws/cocina`.
- Declara entradas con modelos Pydantic y valida reglas de dominio antes de persistir.
- Conserva nombres, tipos y formas de respuesta que consume `frontend/src/api.js` y `frontend/src/App.jsx`. Las respuestas existentes no usan un sobre JSON común.
- Usa `HTTPException` para errores esperados, con estado y mensaje apropiados. No ocultes fallos ni los conviertas en respuestas exitosas.
- Los permisos se verifican en el servidor con dependencias como `Depends(solo(...))`. Valida también que la organización y sucursal autorizadas posean los recursos recibidos.
- Si cambia una ruta o contrato, actualiza el frontend y la documentación funcional en el mismo cambio.

## Autenticación y autorización

- Las contraseñas se almacenan como hashes bcrypt con los helpers de `backend/app/seguridad.py`; nunca guardes ni registres texto claro.
- Usa los helpers de token existentes: JWT HS256 firmado con `JWT_SECRET`, con verificación de firma y expiración.
- El login requiere el código de restaurante y usuario o correo. La búsqueda de usuario debe restringirse por el código de organización correspondiente.
- Conserva los roles `dueno`, `gerente`, `mesero`, `cocinero` y `cajero` y sus permisos efectivos del backend. Los controles de UI no reemplazan la autorización del servidor.
- Para rutas autenticadas, conserva el contexto de organización que la dependencia de base de datos instala en la transacción.

## Sesiones, errores y datos

- La conexión se configura con `DATABASE_URL`; dentro de Compose, el backend usa el rol sin privilegios `app` y el host `db`.
- Para rutas autenticadas, reutiliza la dependencia de sesión existente: instala `app.org_id`, confirma al completar la petición, hace rollback ante excepciones y cierra la sesión.
- Para flujos de autenticación con sesión propia, sigue el patrón `with Sesion() as s:` y confirma explícitamente las escrituras.
- Usa SQLAlchemy 2 y parámetros enlazados. Las sentencias `text()` deben enlazar parámetros; no interpolar datos externos en SQL.
- Usa `Decimal`/`Numeric` para importes y cantidades persistidas. Conserva snapshots históricos de precio y costo por línea de pedido.
- Los cambios de pedido e inventario deben permanecer en la misma transacción; restaura el consumo registrado al modificar o eliminar pedidos autorizados.
- No desactives RLS, no eleves el rol de la aplicación a superusuario ni omitas el aislamiento por sucursal para resolver errores.

Los detalles de esquema, RLS y migraciones están en [database-standards.md](./database-standards.md). Los comandos generales están en [project-context.md](./project-context.md).

## Secretos y fallos

- Lee `DATABASE_URL` y `JWT_SECRET` del entorno. No codifiques ni muestres contraseñas, tokens, secretos o credenciales.
- Captura excepciones específicas cuando corresponda y deja explícito el manejo de errores. No agregues capturas que silencien fallos.
- No registres datos sensibles; los mensajes y logs deben aportar diagnóstico sin exponer credenciales o información personal innecesaria.

## Validación

No se identifica actualmente una suite automatizada de backend en el repositorio. Valida el endpoint o flujo afectado y, cuando corresponda, permisos por rol, aislamiento de organización/sucursal, migraciones y efectos transaccionales.

Desde la raíz, el servicio puede reconstruirse con `docker compose build backend` y consultarse con `docker compose logs -f backend`.
