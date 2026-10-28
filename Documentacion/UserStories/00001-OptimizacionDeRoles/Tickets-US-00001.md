# Tickets para US 00001: Optimizar roles e inicio de sesión

Estos tickets desglosan la historia de usuario [00001-Optimizando-roles](UserStories/00001-Optimizando-roles). Los tickets son propuestas locales en Markdown; no se crearon issues en GitHub.

## T-00001: Inicio de sesión por restaurante

**Prioridad:** Alta
**Tipo:** Backend y frontend

Permitir que una persona inicie sesión proporcionando el código único de su restaurante, username o correo y contraseña.

**Criterios de aceptación**
- El formulario solicita código de restaurante, username/correo y contraseña.
- Los empleados inician con username; el dueño puede usar correo o username (`dueno` en cuentas nuevas, `usuario-<id>` en cuentas migradas).
- El código se genera para restaurantes nuevos y se muestra al dueño; los restaurantes existentes reciben un código al migrar.
- Las credenciales válidas autentican al usuario en el restaurante correcto y conservan su rol y sucursal en la sesión.
- Las credenciales inválidas muestran un mensaje genérico, sin revelar qué dato falló.
- Las contraseñas continúan almacenándose como hashes; nunca se devuelven al cliente.
- El login no permite acceder a datos de otra organización.

**Estado:** Implementado. El username es único case-insensitive por restaurante; el correo del dueño sigue siendo único globalmente.

## T-00002: Administración de usuarios del restaurante

**Prioridad:** Alta
**Tipo:** Frontend y backend

Agregar a dueño y gerente una sección para consultar y crear usuarios de su restaurante.

**Criterios de aceptación**
- La sección lista únicamente usuarios de la organización del administrador.
- El formulario permite capturar nombre, username, contraseña inicial, rol y sucursal cuando aplique; los empleados no necesitan correo.
- Usernames aceptan 3–32 caracteres (`a-z`, `0-9`, punto, guion o guion bajo), sin distinguir mayúsculas.
- Las cuentas existentes reciben `usuario-<id>` al migrar; las contraseñas y correos actuales se conservan.
- Dueño/gerente puede crear gerentes, meseros, cocineros y cajeros, con validación de datos duplicados, rol y sucursal.
- Mesero, cocinero y cajero requieren sucursal asignada; gerente puede operar en todas las sucursales.
- No se permite crear dueños desde esta sección.
- La contraseña no vuelve a mostrarse después de crear al usuario.
- Un usuario de otra organización no puede consultar ni administrar estas cuentas.

**Estado:** Implementado para listado y alta. Editar, desactivar y restablecer credenciales quedan fuera de alcance.

## T-00003: Aplicar matriz de permisos en el backend

**Prioridad:** Alta
**Tipo:** Backend y pruebas

Revisar y completar la autorización de endpoints según la matriz de roles de US 00001. La autorización del servidor es obligatoria aunque la interfaz oculte acciones.

**Criterios de aceptación**
- Cada endpoint protegido permite únicamente los roles autorizados.
- Un usuario sin sesión recibe rechazo de autenticación; un usuario autenticado sin permiso recibe rechazo de autorización.
- Los permisos se aplican dentro de la organización y sucursal asignadas.
- Las pruebas cubren accesos permitidos, denegados y aislamiento entre organizaciones.
- Las peticiones rechazadas no modifican datos.

**Estado:** Implementado con la matriz acordada: gerente equivale a dueño, cocinero es de solo lectura y cajero consulta/cobra.

## T-00004: Mostrar navegación y acciones según el rol

**Prioridad:** Alta
**Tipo:** Frontend

Adaptar la navegación y los controles visibles para que cada persona encuentre solo las funciones correspondientes a su rol.

**Criterios de aceptación**
- Dueño/admin puede consultar las secciones autorizadas y levantar pedidos.
- Mesero ve las herramientas necesarias para gestionar pedidos.
- Cocinero ve pedidos y detalles en solo lectura.
- Cajero ve cuentas abiertas y controles de cobro, sin alta o edición de pedidos.
- La interfaz no se considera una barrera de seguridad: los endpoints siguen validando los permisos.
- La sesión identifica claramente el restaurante, usuario y rol activo.

**Estado:** Implementado en navegación y vistas principales.

## T-00005: Completar gestión de pedidos para meseros

**Prioridad:** Alta
**Tipo:** Backend, frontend y pruebas

Implementar las operaciones de consulta, edición y eliminación de pedidos que faltan para completar la gestión solicitada al mesero.

**Criterios de aceptación**
- Un mesero puede consultar pedidos de su sucursal y crear, editar y eliminar pedidos cuyos platillos sigan pendientes.
- Editar/eliminar se rechaza si cualquier platillo empezó a prepararse o el pedido fue cobrado.
- Dueño/admin puede consultar y crear pedidos según la historia.
- Cocinero puede consultar pedidos y sus detalles, pero no puede crear, editar ni eliminar pedidos.
- Cada operación valida rol, organización, sucursal y estado del pedido en el servidor.
- Las acciones completadas actualizan la vista y los errores se muestran sin perder datos ingresados.

**Estado:** CRUD y reglas de estado implementados; consumo de inventario se restaura al editar/eliminar. Pedidos antiguos sin snapshot de inventario se protegen contra modificación.

## Pendiente para historias futuras

1. Edición, desactivación y restablecimiento de credenciales para usuarios existentes.
2. Recuperación de contraseña y verificación de correo.
