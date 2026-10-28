---
description: "Carga primero las instrucciones y el contexto relevante del proyecto antes de abordar una tarea concreta."
name: "Tomar Contexto"
argument-hint: "<tarea para la que necesitas contexto>"
---

Ayúdame con la siguiente tarea: `${input:task:describe la tarea}`.

Si el mensaje que acompaña a este prompt ya incluye una tarea concreta, usa esa solicitud en lugar de pedirla de nuevo.

## Paso 1: Leer las instrucciones del proyecto

1. Lee íntegramente `aispecs/AGENTS.md` antes de analizar o ejecutar la tarea.
2. Lee `aispecs/README.md` para orientación del stack, arquitectura y comandos cuando sea relevante.
3. Lee `aispecs/rules/base.md` y cualquier instrucción aplicable a los archivos que tocaría la tarea. No inventes reglas por capa si no existen.
4. Comprueba qué documentación de contexto está realmente disponible. El directorio existente es `Documentacion/`; no crees ni asumas una ruta duplicada `Documentación/`. Un README raíz o índice de documentación puede no estar presente: si falta, continúa con los recursos existentes y no lo recrees como parte de tomar contexto.

## Paso 2: Reunir solo el contexto pertinente

- Resume brevemente el objetivo y delimita qué áreas del proyecto involucra la tarea.
- Consulta el índice o documento de orientación disponible, después los documentos funcionales/técnicos directamente relevantes.
- Inspecciona archivos de código, configuración o datos relevantes antes de concluir. Usa búsquedas acotadas y sigue referencias concretas; no leas indiscriminadamente respaldos, secretos, dependencias generadas o archivos ajenos.
- Stack de referencia a confirmar con los archivos del repositorio: Python 3.12/FastAPI/SQLAlchemy/PostgreSQL en `backend/`; React/JavaScript/Vite en `frontend/`; inicialización PostgreSQL en `db/`; proxy Caddy en `proxy/`; composición en Docker Compose.
- Para cambios de esquema, consulta modelos y migraciones en `backend/app/modelos.py` y `backend/app/migraciones.py`. Para API, autenticación y permisos, revisa `backend/app/main.py` y `backend/app/seguridad.py`. Para integración frontend, revisa `frontend/src/api.js` y los componentes relacionados.
- Para historias, tickets o planes, busca en `Documentacion/UserStories/` y lee la fuente específica, sin asumir una estructura de carpetas fija.
- En tareas con datos, autorización o flujos operativos, considera aislamiento por organización/sucursal, RLS, roles, transacciones e historial de costos/inventario únicamente si aplican.

## Paso 3: Actuar con el contexto reunido

- Una vez que tengas contexto suficiente, ejecuta la tarea pedida; no te limites a enumerar archivos consultados.
- Si hay ambigüedad que pueda afectar comportamiento, datos, seguridad o alcance, pide aclaración antes de realizar cambios. Para asuntos menores no bloqueantes, adopta el patrón existente más conservador y dilo en el resumen.
- Respeta los cambios previos del worktree. No borres, reemplaces ni reviertas archivos no relacionados.
- Verifica el resultado con las pruebas, build o comandos focalizados que existan para la parte cambiada. Informa claramente lo que no pudo ejecutarse.
- Si el usuario solo pidió recopilar contexto y no describió una tarea de implementación, entrega un resumen breve de arquitectura y archivos relevantes sin modificar nada.

## Respuesta

Resume el contexto relevante, el trabajo realizado (si aplica), los archivos modificados y las validaciones ejecutadas o pendientes. No afirmes que inspeccionaste documentación o ejecutaste comandos que no consultaste.
