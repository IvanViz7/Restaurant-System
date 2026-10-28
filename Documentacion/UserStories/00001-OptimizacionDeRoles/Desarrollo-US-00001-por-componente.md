# Desarrollo por componente: US 00001

Este desglose complementa el [plan general](Plan-US-00001.md) y los [tickets](Tickets-US-00001.md). Las decisiones de producto ya están cerradas; aquí se registra qué componentes se implementaron y qué validación falta.

## Componente 0: Producto y contratos

**Objetivo:** fijar reglas que afectan simultáneamente al esquema, la API y la interfaz.

**Trabajo**
- Aprobar la matriz `rol × recurso × acción` para dueño, gerente, mesero, cocinero y cajero.
- Decidir cómo se identifica el restaurante durante el login.
- Definir reglas de username y correo: empleados usan username; dueño admite username o correo.
- Definir permisos de cocina sobre estados de preparación.
- Definir qué estados permiten editar o eliminar pedidos.
- Definir si se pueden editar, desactivar o restablecer credenciales de usuarios existentes.
- Especificar solicitudes y respuestas de login, usuario y operaciones de pedidos.

**Estado:** completado. Login por código + username para empleados y username/correo para dueño; username único case-insensitive por restaurante; gerente equivale a dueño; cocinero queda en solo lectura; cajero consulta/cobra; pedidos se editan/eliminan solo antes de preparación/cobro.

## Componente 1: Persistencia y migraciones

**Archivos probables:** `backend/app/modelos.py`, `backend/app/db.py`, nueva configuración y revisiones de migración.

**Trabajo**
- **Implementado:** migraciones SQL numeradas en `backend/app/migraciones.py`, registradas en `schema_migrations` y protegidas con advisory lock.
- **Implementado:** código único de organización; correos existentes conservan unicidad global y empleados tienen username único por organización.
- **Implementado:** `usuario-<id>` para cuentas existentes, `dueno` para dueños nuevos; el email sigue disponible como acceso alternativo.
- **Implementado:** snapshot de consumo de inventario por línea de pedido para permitir restauración segura.
- **Pendiente:** decidir si se adopta Alembic u otra herramienta formal, y documentar reversión/recuperación.

**Validación**
- **Pasó:** migraciones 0001, 0002 y 0003 aplicadas sobre la base existente; se verificaron columnas, usernames y versiones.
- **Pendiente:** prueba automatizada desde cero, duplicados/errores y recuperación ante migración fallida.

**Dependencia:** Componente 0 completado.

## Componente 2: Backend de autenticación y usuarios

**Archivos probables:** `backend/app/main.py`, `backend/app/seguridad.py`, `backend/app/modelos.py`.

**Trabajo**
- **Implementado:** `/api/auth/login` recibe código y username o correo; `/api/auth/registro` genera código y asigna username `dueno`.
- **Implementado:** `/api/auth/me` actualiza sesiones existentes con organización/código, sin volver a registrar.
- **Implementado:** `/api/usuarios` lista y crea cuentas; `/api/sucursales` lista sucursales permitidas.
- **Implementado:** hashing, error genérico, validación de roles, username y sucursal; no se devuelven secretos.

**Validación**
- **Pasó manualmente:** alta de empleados sin email, unicidad de username por restaurante y login de empleado/dueño.
- **Pendiente:** suite persistente para login inválido, sesión vencida y aislamiento entre organizaciones.

**Dependencia:** Componentes 0 y 1.

## Componente 3: Autorización y pedidos en backend

**Archivos probables:** `backend/app/main.py`, configuración de pruebas y utilidades de autorización.

**Trabajo**
- **Implementado:** autorización por rol en lecturas/escrituras y en websocket de cocina.
- **Implementado:** `PATCH`/`DELETE /api/pedidos/{id}` con organización, sucursal, estado, inventario y reglas de preparación.
- **Implementado:** cocinero puede leer cocina, pero no mutar estados; cajero solo consulta/cobra.
- **Implementado:** cobro limitado a cuentas abiertas en la sucursal del usuario.

**Validación**
- **Pasó manualmente:** permisos dueño/mesero/cocinero/cajero, CRUD, restauración de inventario y bloqueo tras cobro.
- **Pendiente:** pruebas persistentes de tenant cruzado, sucursal incorrecta y mutación rechazada sin side effects.

**Dependencia:** Componentes 0 y 1. Puede desarrollarse junto con el Componente 2 una vez acordada la matriz.

## Componente 4: Frontend de acceso y administración

**Archivos probables:** `frontend/src/App.jsx`, `frontend/src/api.js` y componentes nuevos si se separa la pantalla actual.

**Trabajo**
- **Implementado:** login por código y username/correo; cabecera muestra restaurante, usuario, rol y código.
- **Implementado:** refresh de sesiones antiguas mediante `/api/auth/me`.
- **Implementado:** sección Usuarios con listado/alta, y navegación/actions filtradas por rol.
- **Implementado:** cocinero en solo lectura; mesero y cajero ven las acciones respectivas.
- **Pendiente:** mejorar estados de carga y feedback para errores `401`/`403` en formularios no cubiertos.

**Pruebas**
- Formularios válidos e inválidos y mensajes de error.
- Secciones/acciones visibles por rol.
- Alta y listado de usuarios con estados vacíos, carga y error.
- Verificar que las contraseñas no se muestran en listas ni logs de interfaz.

**Dependencia:** contratos del Componente 0 y endpoints de Componentes 2 y 3.

## Componente 5: Frontend de pedidos y cocina

**Archivos probables:** `frontend/src/App.jsx`, `frontend/src/api.js` y componentes nuevos para pedidos/cocina.

**Trabajo**
- **Implementado:** creación/consulta/edición/eliminación por dueño, gerente y mesero.
- **Implementado:** confirmación de eliminación; bloquear edición/borrado tras iniciar preparación o cobrar.
- **Implementado:** snapshot y restauración de inventario en las operaciones permitidas.
- **Implementado:** vistas de cocina y cuentas/cobro por rol.

**Pruebas**
- Flujo completo de creación, consulta, edición y eliminación según rol.
- Restricciones según estado de preparación/cobro.
- Errores de servidor, carga y actualización de interfaz.

**Dependencia:** contratos y permisos de Componentes 0 y 3.

## Componente 6: Pruebas integrales y operación

**Archivos probables:** nuevas carpetas de pruebas backend/frontend, `docker-compose.yml` y `README.md`.

**Trabajo**
- **Pasó:** build Docker backend/frontend y batería temporal de integración para login, roles, pedidos e inventario.
- **Pasó:** tenant temporal limpiado tras la prueba; tenant existente preservado.
- **Pendiente:** añadir pruebas automatizadas mantenidas y completar guía de migración/recuperación.
- **Implementado:** frontend usa `npm ci` con lockfile y Docker ignora `node_modules`/`dist`.

**Criterio de salida**
- Los criterios de US 00001 tienen pruebas automatizadas o pasos manuales repetibles.
- La migración pasa en base vacía y existente.
- Los roles y el aislamiento de organización/sucursal se prueban mediante llamadas directas a la API, no solo desde la interfaz.
- Los flujos de dueño, mesero y cocinero funcionan según la matriz aprobada; gerente y cajero quedan cubiertos según la decisión de producto.

**Dependencia:** Componentes 1 a 5.

## Secuencia de integración

1. Componente 0 aprobó decisiones y contratos.
2. Componente 1 aplicó las migraciones versionadas.
3. Componentes 2 y 3 implementaron autenticación y autorización.
4. Componentes 4 y 5 integraron la experiencia por rol.
5. Componente 6 ejecutó build y batería manual; falta convertir cobertura en suite persistente.
