# Plan de implementación: US 00001

Fuente: [US 00001 - Optimizar roles e inicio de sesión](UserStories/00001-Optimizando-roles)
Desglose: [Tickets de US 00001](Tickets-US-00001.md)

## Objetivo
Implementar inicio de sesión por restaurante y autorización consistente por rol, organización y sucursal; habilitar administración de usuarios y las operaciones de pedidos definidas en la historia.

## Estado actual relevante
- Roles: `dueno`, `gerente`, `mesero`, `cocinero` y `cajero`; gerente comparte permisos de dueño, cocinero es de solo lectura y cajero consulta/cobra.
- El login usa código de restaurante y username o correo; usernames son únicos case-insensitive por restaurante y los correos siguen siendo globalmente únicos.
- Dueños nuevos reciben username `dueno`; cuentas existentes reciben `usuario-<id>` mediante la migración 0003.
- Las migraciones versionadas `0001_codigo_restaurante`, `0002_consumo_pedido_items` y `0003_usuario_empleados` se ejecutaron sobre la base existente.
- Usuarios puede listar/crear desde UI para dueño/gerente; pedidos tiene CRUD para estados permitidos y snapshots de consumo para restituir inventario.
- La autorización se aplica en backend además de filtrar la navegación; empleados operativos quedan limitados a su sucursal.
- No existía suite automatizada. Se ejecutó una batería temporal de integración para login, permisos por rol, CRUD, inventario y bloqueo tras cobro; falta convertirla en pruebas persistentes.

## Decisiones cerradas
- Identificador de acceso: código único + username para empleados; dueño admite username (`dueno` nuevo, `usuario-<id>` existente) o correo.
- Empleados no requieren email; las cuentas existentes conservan email/contraseña y reciben `usuario-<id>` como username.
- Gerente tiene permisos de dueño; dueño/gerente solo listan y crean usuarios, no crean otro dueño.
- Cocinero puede consultar pedidos, pero no cambiar contenido ni estado de preparación.
- Cajero puede consultar cuentas abiertas y cobrarlas, sin gestionar pedidos.
- Editar/eliminar pedidos se permite solo mientras todos sus platillos estén pendientes y antes del cobro.

## Fases

### Fase 0: Cerrar decisiones de producto (completada)
La matriz de roles y los contratos de login, usuarios y pedidos están definidos en US 00001.

**Salida:** decisiones aprobadas y documentadas.

### Fase 1: Preparar esquema y pruebas
- **Implementado:** migraciones SQL versionadas en `backend/app/migraciones.py`; organizaciones existentes reciben código `rest-<id>` y el consumo de pedido se conserva por línea.
- **Pendiente:** integrar migraciones con una herramienta/flujo formal, y crear base aislada, fixtures y suite persistente.

**Salida:** migración probada sobre la base existente; cobertura automatizada pendiente.

### Fase 2: Login y sesión por organización
Relacionado con T-00001.
- **Implementado:** login por código + username o correo; empleados sin correo y dueño por username/correo; `/auth/me` actualiza sesiones existentes.
- **Implementado:** hash de contraseñas y mensaje genérico de fallo.
- **Pendiente:** pruebas automatizadas persistentes de credenciales e aislamiento.

**Salida:** contrato integrado en frontend/backend; verificación automatizada pendiente.

### Fase 3: Matriz de autorización en backend
Relacionado con T-00003.
- **Implementado:** roles aplicados a lectura, creación, edición, eliminación, usuarios, cocina y cobro.
- **Implementado:** operaciones de empleados limitadas a sucursal asignada; RLS sigue aplicando aislamiento de organización.
- **Verificación manual pasada:** permisos de dueño, mesero, cocinero y cajero; añadir casos automatizados y tenant cruzado a la suite.

**Salida:** permisos seguros aunque se invoquen endpoints directamente sin usar la interfaz.

### Fase 4: Administración de usuarios
Relacionado con T-00002.
- **Implementado:** vista Usuarios para dueño/gerente, con listado y alta.
- **Implementado:** username validado y único por restaurante, hash de contraseña y sucursal obligatoria para mesero/cocinero/cajero.
- **Fuera de alcance:** editar, desactivar o restablecer usuarios existentes.
- **Pendiente:** pruebas automatizadas de límites entre organizaciones y errores de formulario.

**Salida:** un administrador puede preparar cuentas del equipo sin acceso a otras organizaciones.

### Fase 5: Interfaz por rol y pedidos
Relacionado con T-00004 y T-00005.
- **Implementado:** login por código y username/correo, cabecera con organización/usuario/rol/código y navegación filtrada.
- **Implementado:** cuentas de pedidos para dueño/gerente/mesero/cajero; CRUD de pedidos para roles autorizados.
- **Implementado:** edición/eliminación solo antes de preparar/cobrar y restauración del inventario mediante snapshots.
- **Implementado:** cocinero consulta cocina en modo solo lectura; cajero cobra sin crear pedidos.
- **Pendiente:** ampliar estados de carga/error y cobertura E2E.

**Salida:** cada rol puede completar únicamente los flujos autorizados desde la interfaz.

### Fase 6: Regresión y despliegue
- **Pasó:** builds Docker backend/frontend y batería temporal de integración de login, permisos, CRUD, inventario y bloqueo de pedidos cobrados.
- **Pasó:** migración aplicada sobre la base existente; se confirmó preservación del tenant previo.
- **Pendiente:** convertir la batería temporal en pruebas mantenidas, probar base vacía y flujo de migración fallido, y documentar recuperación.

**Salida:** versión desplegable con los criterios de aceptación de US 00001 cubiertos.

## Orden y dependencias
`Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fases 4 y 5 → Fase 6`

La Fase 3 puede desarrollarse en paralelo con la Fase 2 una vez aprobada la matriz, pero su integración depende de que el token mantenga una identidad y organización inequívocas. Las fases 4 y 5 requieren la matriz de permisos final.

## Criterios de terminado
- Todos los criterios de aceptación de US 00001 tienen pruebas automatizadas o una verificación manual documentada.
- Ningún acceso depende únicamente de ocultar controles en frontend.
- El aislamiento entre organizaciones y sucursales está probado para permisos permitidos y denegados.
- La migración funciona con datos existentes y no almacena contraseñas en texto plano.
- La documentación permite configurar y desplegar el flujo actualizado.
