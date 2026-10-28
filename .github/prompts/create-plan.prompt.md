---
description: "Genera planes de desarrollo verificables a partir de tickets de una historia de usuario, adaptados al stack y documentación de este repositorio."
name: "Create Development Plan"
argument-hint: "<historia o ticket> [database|backend|frontend]"
---

Crea planes de desarrollo verificables para el identificador de historia o ticket indicado aquí: `${input:task:historia o ticket [database|backend|frontend]}`.

Si el mensaje que acompaña a este prompt ya especifica claramente la historia/ticket y la capa opcional, usa esa entrada y no vuelvas a pedirla.

## Reglas del repositorio

- Antes de empezar, lee `aispecs/AGENTS.md` y aplica sus reglas.
- Usa `Documentacion/UserStories/` como ruta real de las historias en esta copia del repositorio. No crees ni uses una carpeta duplicada `Documentación/`.
- Confirma la estructura y el contenido de los archivos encontrados; no asumas que existe un directorio `tickets/` ni un `ticket.md` por capa. Actualmente, los tickets pueden estar agrupados por secciones `T-<id>` en un archivo `Tickets-US-<id>.md`.
- No modifiques código, tickets ni planes existentes distintos de los archivos de plan que vas a generar.

## Argumentos

La entrada contiene el identificador de una historia o ticket y, opcionalmente, una capa:

| Formato | Resultado |
|---|---|
| `<historia>` | Generar planes por ticket para todas las capas aplicables |
| `<historia> database` o `<historia> db` | Generar solo los planes de base de datos aplicables |
| `<historia> backend` o `<historia> be` | Generar solo los planes de backend aplicables |
| `<historia> frontend` o `<historia> fe` | Generar solo los planes de frontend aplicables |
| `<ticket> [capa]` | Generar el plan o planes del ticket indicado |

El primer argumento puede ser el identificador numérico (`00001`), el nombre de carpeta/título o el ID del ticket (`T-00001`). Si el argumento puede referirse a más de una historia o ticket, pide precisión antes de escribir archivos.

## Paso 1: Encontrar y leer la fuente

1. Busca dentro de `Documentacion/UserStories/` la historia que coincida por identificador, nombre de carpeta o título. Lee su contenido y la documentación asociada que aporte criterios, decisiones, dependencias o alcance.
2. Encuentra el archivo de tickets de esa historia (por ejemplo, `Tickets-US-00001.md`) y lee el documento completo para identificar cada sección de ticket y sus criterios de aceptación.
3. Si se indicó un ID `T-...`, limita la generación a ese ticket. Si no existe, informa el problema y ofrece los IDs disponibles.
4. Si no hay coincidencia única de historia, muestra las carpetas/títulos candidatos y solicita aclaración. No inventes tickets ni criterios.
5. Si faltan tickets, criterios o documentos mencionados, indícalo y continúa solo cuando la información disponible permita un plan útil; marca explícitamente cualquier supuesto.

## Paso 2: Decidir las capas aplicables

Las capas válidas son `database`, `backend` y `frontend`.

- Sin filtro, genera un plan para cada capa realmente implicada por cada ticket. Usa el campo **Tipo**, el alcance y los criterios; si el ticket no tiene campo **Tipo**, infiere la capa por el trabajo solicitado y señala la inferencia.
- Con filtro, genera únicamente esa capa cuando el ticket la implique. Si no la implica, informa que no hay trabajo de esa capa y no crees un plan vacío.
- `database` incluye cambios de esquema, modelos, índices, restricciones y migraciones PostgreSQL. En este proyecto, las migraciones versionadas se implementan en `backend/app/migraciones.py`; no inventes una carpeta de scripts SQL.
- `backend` incluye API FastAPI, autenticación, permisos, lógica de negocio y persistencia en SQLAlchemy.
- `frontend` incluye la interfaz React, integración con API y estilos.
- Un ticket que abarque varias capas debe tener planes separados por capa. Mantén en cada plan las tareas y criterios pertinentes a esa capa; no dupliques todas las tareas en todos los planes.
- No deduzcas que una funcionalidad ya está pendiente solo porque aparece en un ticket: revisa el estado descrito y el código/documentación relacionado. Distingue entre trabajo existente, trabajo faltante y verificación pendiente, sin marcar tareas completadas por el usuario.

## Paso 3: Crear los planes

Guarda cada plan en la misma carpeta que el archivo fuente de tickets, sin sobrescribir `Plan-US-<id>.md` ni otros planes de historia:

- Tickets agrupados en `Tickets-US-<id>.md`: `Plan-T-<ticket-id>-<capa>.md` (por ejemplo, `Plan-T-00001-backend.md`).
- Ticket en un archivo independiente: `Plan-<nombre-del-ticket>-<capa>.md`, con nombre breve y estable.

Si un archivo de plan con ese mismo nombre ya existe, reemplázalo. No sobrescribas planes de otras capas o tickets.

Cada plan debe ser concreto, ejecutable y tener esta estructura:

```markdown
---
ticket: <ruta relativa al archivo fuente de tickets>
story: <identificador y título de la historia>
ticket-id: <ID del ticket>
layer: <database|backend|frontend>
depends-on: <ruta(s) relativa(s) a tickets o "none">
progress: 0 / <total> tasks completed
---

# Plan de desarrollo — [<DB|BE|FE>] <título del ticket>

> Marca cada tarea como `- [x]` al completarla y actualiza `progress`.

## Fase 1 · Alcance y dependencias
- [ ] Revisar el ticket, sus criterios de aceptación y las decisiones/documentos relacionados.
- [ ] Confirmar las dependencias explícitas del ticket; no inventar bloqueos.

## Fase 2 · Implementación
<!-- Sustituye por tareas específicas, agrupadas por archivos/componentes reales del repositorio. -->

## Fase 3 · Pruebas y verificación
<!-- Añade tareas verificables por criterio de aceptación y por riesgo de esta capa. -->

## Fase 4 · Documentación y cierre
- [ ] Actualizar la documentación funcional/técnica afectada por cambios de contrato o comportamiento.
- [ ] Revisar el diff y confirmar que no se modificaron archivos fuera del alcance.
```

### Criterios para las tareas

- Usa una casilla `- [ ]` para cada acción comprobable. Divide los cambios grandes en tareas pequeñas y ordenadas; incluye prerrequisitos solo si son necesarios.
- Incluye una tarea de implementación por cada comportamiento o restricción relevante del ticket y una tarea de verificación por cada criterio de aceptación. Mantén las referencias al criterio claras en el texto.
- Para cambios de base de datos, inspecciona el esquema/modelos/migraciones actuales y plantea una nueva versión idempotente en `backend/app/migraciones.py` cuando corresponda. Incluye compatibilidad con datos existentes y verificación de la migración; no propongas `create_all()` como sustituto de migraciones.
- Para backend, incluye validación del servidor, autenticación/autorización y límites de organización/sucursal cuando sean pertinentes; las restricciones de la interfaz no sustituyen controles del backend.
- Para frontend, considera integración mediante `frontend/src/api.js`, estados de carga/error y visibilidad por rol cuando aplique. La ocultación de controles no se considera autorización.
- En cambios de pedidos/inventario, incluye las reglas pertinentes de estado, transacciones, snapshots y restauración del consumo; no alteres el historial de precio/costo.
- En cambios sensibles, agrega verificación de permisos permitidos/denegados, aislamiento multi-tenant y ausencia de efectos secundarios en solicitudes rechazadas.
- Usa nombres de archivo y componentes existentes cuando estén confirmados; si un archivo nuevo aún no se puede determinar, describe el área sin inventar una ruta concreta.
- No asumas herramientas o pruebas que no existen. En esta copia no hay una suite automatizada persistente: propone pruebas persistentes si el ticket lo requiere; para cambios frontend puedes considerar `npm run build` en `frontend/`, y para integración usa Docker Compose solo si el entorno y la tarea lo permiten. No afirmes que se ejecutaron validaciones.
- No agregues tareas genéricas para crear ramas, hacer push, abrir PR o hacer commit.
- El `progress` inicial debe ser `0 / N tasks completed`, donde `N` es el número exacto de todas las casillas `- [ ]` del archivo, incluidas las fases de alcance y cierre.
- No dejes placeholders, comentarios HTML, secciones vacías ni tokens `<...>` en los planes finales. Sustituye la plantilla por contenido adaptado al ticket.

## Paso 4: Confirmar

Al terminar, informa la historia y cada plan creado con su capa y número de tareas. Enumera los tickets/capas omitidos y el motivo (por ejemplo, capa no aplicable o fuente faltante). No declares pruebas ejecutadas si solo fueron incluidas en el plan.
