---
description: "Desglosa una historia de usuario suficientemente definida en tickets de implementación verificables para el stack de este proyecto."
name: "Create Implementation Tickets"
argument-hint: "<historia o archivo de historia>"
---

Crea tickets de implementación a partir de la historia de usuario indicada aquí: `${input:story:identificador, nombre o ruta de la historia}`.

Si el mensaje que acompaña a este prompt ya identifica claramente la historia, úsalo y no vuelvas a solicitar el dato.

## Reglas del repositorio

- Antes de empezar, lee íntegramente `aispecs/AGENTS.md` y sigue sus indicaciones.
- Usa `Documentacion/UserStories/`, que es el nombre de carpeta existente en este repositorio. No crees una carpeta duplicada `Documentación/`.
- Respeta el stack actual: Python 3.12, FastAPI, SQLAlchemy 2, PostgreSQL 16, React 18, JavaScript, Vite y Docker Compose.
- Las migraciones para cambios de esquema van en nuevas versiones idempotentes de `backend/app/migraciones.py`; no supongas que existen migraciones SQL separadas.
- Mantén los tickets en español y usa los nombres del dominio, roles y contratos existentes cuando apliquen.
- Este prompt crea documentación de tickets, no implementa código, crea planes de desarrollo, abre issues ni modifica la historia de usuario.

## Paso 1: Encontrar y validar la historia

1. Busca dentro de `Documentacion/UserStories/` una coincidencia por identificador, nombre de carpeta, título o ruta proporcionados.
2. Lee el archivo que contiene la historia y cualquier documentación cercana que especifique decisiones, alcance o dependencias. La estructura puede tener un archivo de historia directamente en la carpeta o anidado en `UserStories/<slug>`; no asumas una ubicación fija.
3. Si hay varias coincidencias posibles, muestra sus rutas y solicita al usuario que elija. No adivines.
4. Considera que la historia está suficientemente definida si explica el objetivo/valor para el usuario y contiene requisitos o criterios de aceptación concretos que se puedan convertir en trabajo y verificar. No exijas literalmente un encabezado `## [enhanced]`: las historias actuales del repositorio usan encabezados en español.
5. Si faltan objetivo, comportamiento esperado o criterios verificables, no inventes requisitos ni crees tickets todavía. Enumera las lagunas y solicita que el usuario complete o confirme la información. Las preguntas abiertas que no bloquean la implementación pueden registrarse como pendientes dentro de los tickets.
6. Lee tickets existentes y documentación técnica relacionada para identificar el estado actual y evitar duplicar trabajo ya implementado. No marques implementación como pendiente si la historia o el código indican que ya existe; crea tickets de trabajo faltante o de pruebas persistentes si eso sigue siendo necesario.

## Paso 2: Desglosar el trabajo

- Divide la historia en el menor conjunto de tickets cohesivos que cubra sus requisitos, dependencias técnicas y criterios de aceptación. No uses automáticamente un ticket por capa: un ticket puede abarcar varias capas cuando una misma capacidad necesite cambios coordinados.
- Conserva trazabilidad: cada ticket debe referirse a uno o más criterios de aceptación de la historia, y el conjunto de tickets debe cubrir todos los criterios incluidos en alcance.
- Clasifica el **Tipo** con una o más capas de esta lista: `Database`, `Backend`, `Frontend`, `Pruebas`, `Documentación`. No agregues capas sin trabajo real.
- Database se refiere a cambios de esquema, restricciones, índices o migraciones. Los cambios exclusivamente de lógica con el esquema actual pertenecen a Backend.
- Considera seguridad y reglas existentes cuando sean pertinentes: autorización en el servidor, aislamiento multi-tenant por `organizacion_id`/RLS, aislamiento de sucursal, roles `dueno`, `gerente`, `mesero`, `cocinero` y `cajero`, hashes de contraseña, y reglas de pedidos/inventario e historial de costos. No añadas requisitos ajenos al objetivo de la historia.
- No plantees ocultar controles en React como sustituto de autorización backend.
- Si la historia requiere cambiar el esquema existente, el ticket debe pedir una migración versionada, compatible con datos existentes e idempotente en `backend/app/migraciones.py`; `Base.metadata.create_all()` no sustituye esa migración.
- Incluye pruebas concretas apropiadas al riesgo y alcance. No asumas que existe una suite automatizada persistente: si se necesita cobertura mantenida y no existe, inclúyela como trabajo; distingue pruebas nuevas de comandos de build disponibles.
- Evita rutas, nombres de módulos, endpoints, campos, tablas, comportamientos o dependencias inventados. Usa archivos existentes cuando estén confirmados; para decisiones de implementación aún abiertas, describe el resultado requerido y deja la solución técnica abierta.
- Las preguntas pendientes que afecten seguridad, permisos, datos, alcance o criterios de aceptación bloquean la generación hasta que el usuario las aclare. Las decisiones no bloqueantes se registran como **Pendientes por definir** y no se convierten en hechos.

## Paso 3: Crear el documento de tickets

Guarda el documento junto a la historia en la carpeta principal de esa historia:

`Documentacion/UserStories/<carpeta-de-la-historia>/Tickets-US-<id>.md`

Usa el patrón de documento agrupado que ya existe en el repositorio (`Tickets-US-00001.md` con secciones `T-00001`, `T-00002`, etc.), no crees por defecto `tickets/database/ticket.md`, `tickets/backend/ticket.md` ni otras carpetas nuevas.

- Si el archivo `Tickets-US-<id>.md` no existe, créalo.
- Si ya existe, no lo sobrescribas ni lo modifiques silenciosamente. Lee su contenido y presenta un resumen de lo que ya contiene; solicita confirmación para actualizar/combinar el archivo, o crea una propuesta separada `Tickets-US-<id>-propuesta.md` solo si el usuario así lo elige.
- No reemplaces planes, historias, tickets de otras historias ni archivos que no pertenezcan a esta acción.

## Plantilla

```markdown
# Tickets para US <id>: <título de la historia>

Estos tickets desglosan la historia de usuario [<id> - <título>](<ruta relativa a la historia>).

## T-<id-secuencial>: <título orientado al resultado>

**Prioridad:** Alta | Media | Baja
**Tipo:** <una o más capas aplicables>
**Criterios de aceptación relacionados:** <IDs/números exactos de la historia>
**Dependencias:** <IDs de tickets o "Ninguna">

<Descripción breve del resultado que debe obtener el usuario y el alcance de este ticket.>

**Criterios de aceptación**
- <Resultado observable y comprobable>
- <Validaciones, permisos, errores o límites relevantes para este ticket>
- <Pruebas o evidencia de verificación requerida>

**Fuera de alcance**
- <Elemento explícitamente excluido, si aplica>

**Pendientes por definir**
- <Pregunta no bloqueante que requiere decisión, si aplica>

**Estado:** Propuesto
```

Adapta la plantilla: omite las secciones opcionales si no aportan información. No dejes texto entre `<...>`, criterios vagos, secciones vacías ni listas genéricas de tareas de implementación disfrazadas de criterios.

### Calidad y numeración

- Inspecciona los IDs existentes y empieza después del mayor ID `T-xxxxx` ya utilizado para esta historia; no reutilices IDs ni cambies los IDs de tickets previos.
- En la primera generación, numera secuencialmente desde `T-00001`.
- Prioriza según dependencias, riesgo y valor funcional; explica dependencias con IDs de ticket reales.
- Los criterios de aceptación del ticket deben poder comprobarse observando una respuesta/API, un cambio de datos controlado, una interfaz o una prueba. Incluye casos permitidos y denegados cuando haya autorización.
- No copies toda la historia en cada ticket. Conserva solo contexto necesario y referencia los criterios originales.
- Añade al final una sección breve **Pendiente para historias futuras** solo para requisitos expresamente fuera de alcance que la historia señale como futuro; no conviertas preguntas abiertas en compromisos.

## Paso 4: Confirmar

Después de crear el documento, informa:

- Identificador y título de la historia.
- Ruta del archivo creado.
- IDs, títulos y tipos de los tickets.
- Criterios de aceptación cubiertos y cualquier criterio no cubierto con su razón.
- Preguntas o decisiones pendientes.

No afirmes que se ejecutaron pruebas: los tickets solo describen el trabajo y la verificación necesarios.
