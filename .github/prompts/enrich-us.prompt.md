---
description: "Analiza y enriquece una historia de usuario existente con una especificación verificable y alineada con la arquitectura de este proyecto."
name: "Enrich User Story"
argument-hint: "<identificador, nombre o ruta de la historia>"
---

Analiza y enriquece la historia de usuario indicada aquí: `${input:story:identificador, nombre o ruta de la historia}`.

Si el mensaje que acompaña a este prompt ya identifica claramente la historia, úsalo y no vuelvas a solicitarla.

## Reglas del repositorio

- Antes de empezar, lee íntegramente `aispecs/AGENTS.md` y sigue sus indicaciones.
- Usa `Documentacion/UserStories/`, que es el nombre de carpeta existente; no crees ni uses una carpeta duplicada `Documentación/`.
- Respeta el stack actual: Python 3.12, FastAPI, SQLAlchemy 2, PostgreSQL 16, React 18, JavaScript, Vite y Docker Compose.
- Las migraciones de esquema existentes se versionan en `backend/app/migraciones.py`; no describas una estructura de migraciones que el repositorio no usa.
- Mantén el contenido original de la historia intacto. Este prompt actualiza documentación de la historia; no crea tickets, planes ni código.

## Paso 1: Encontrar la historia

1. Busca bajo `Documentacion/UserStories/` una coincidencia por identificador, nombre de carpeta, título o ruta.
2. Lee el archivo completo que contiene la historia y, cuando ayude a entender el alcance, los planes, tickets y documentos próximos.
3. La historia puede estar anidada (por ejemplo, en `UserStories/<slug>`) y no necesariamente llamarse `UserStory.md`. Inspecciona la estructura existente y no asumas nombres de archivo.
4. Si hay varias coincidencias, presenta rutas y títulos candidatos y pide que el usuario elija. Si no hay coincidencias, lista las historias disponibles y solicita precisión. No generes una historia nueva por conjetura.
5. Si el usuario no indicó una historia identificable, solicita el identificador, nombre o ruta antes de editar.

## Paso 2: Analizar el contexto real

- Identifica objetivo, actores, flujos, reglas de negocio, criterios de aceptación, límites y elementos fuera de alcance ya expresados.
- Contrasta solo las partes pertinentes del código y la documentación para identificar entidades, rutas API, estructuras de datos, permisos y componentes existentes. Reutiliza nombres confirmados; no inventes endpoints, tablas, campos, archivos ni pantallas.
- Considera, si son pertinentes a la historia: aislamiento multi-tenant por `organizacion_id` y RLS; límites de sucursal; permisos verificados en backend; roles `dueno`, `gerente`, `mesero`, `cocinero` y `cajero`; hash de contraseñas; y reglas de pedidos, costos históricos e inventario.
- Si la historia necesita una decisión de producto, seguridad, permisos, datos o alcance para quedar implementable, detente y pregunta antes de modificar el archivo. No uses un valor supuesto como si estuviera acordado.
- Las preguntas no bloqueantes pueden conservarse bajo **Pendientes por definir**. Separa claramente hechos existentes, requisitos nuevos propuestos y asuntos pendientes.

## Paso 3: Preparar la especificación enriquecida

Redacta una versión que, según aplique, precise:

- Problema, objetivo, actores y resultado esperado para el usuario.
- Flujo normal y escenarios alternativos o errores relevantes.
- Reglas de negocio, estados, restricciones, validaciones, permisos y límites de organización/sucursal.
- Datos de entrada y salida, datos persistidos y efecto en entidades existentes.
- Contratos de API (método, ruta y forma de solicitud/respuesta) solo cuando estén establecidos por la historia o confirmados en el código. Marca como propuesta cualquier contrato nuevo y no lo presentes como existente.
- Cambios requeridos por capa: `Database`, `Backend`, `Frontend`, `Pruebas` y/o `Documentación`, limitados a lo que la historia necesita.
- Criterios de aceptación numerados, observables y comprobables, incluyendo casos permitidos/denegados cuando aplique.
- Requisitos no funcionales de seguridad, aislamiento, consistencia de datos, accesibilidad o rendimiento solo cuando sean pertinentes y respaldados por la historia.
- Fuera de alcance y preguntas abiertas sin convertirlas en compromisos.

No agregues capas por formalidad ni propongas herramientas que no estén en el stack. Si se requiere cambiar tablas existentes, indica que el esquema debe actualizarse con una migración versionada, idempotente y compatible con datos existentes en `backend/app/migraciones.py`; `Base.metadata.create_all()` no sustituye la migración.

## Paso 4: Actualizar el archivo sin perder el original

Usa el mismo archivo que contiene la historia:

- Si aún no tiene secciones `## [original]` y `## [enhanced]`, conserva su contenido original íntegro bajo `## [original]` y agrega la especificación bajo `## [enhanced]`.
- Si ya contiene ambas secciones, no alteres ningún byte de `## [original]`; actualiza únicamente el contenido de `## [enhanced]`.
- Si solo existe `## [original]`, agrega `## [enhanced]` sin modificar el original.
- Si el archivo ya incluye una versión enriquecida sin estas etiquetas o la ubicación de los límites no es inequívoca, no la sobrescribas: informa la situación y solicita confirmación sobre cómo preservarla.
- Conserva título, enlaces y demás contenido ajeno a la historia cuando sea posible. Antes de guardar, compara la sección original con la fuente para asegurar que no cambió.

Formato objetivo:

```markdown
# <Título existente>

## [original]

<Texto fuente preservado exactamente>

## [enhanced]

<Especificación enriquecida>
```

Adapta el formato si el archivo existente contiene metadatos o estructura que deban preservarse. No dupliques una sección ni borres contenido ajeno.

## Paso 5: Confirmar

Informa:

- Archivo actualizado.
- Resumen de lo precisado (flujos, datos, permisos, contratos o capas relevantes).
- Preguntas o decisiones pendientes.
- Siguiente paso sugerido: `/create-tickets <identificador de historia>`.

No afirmes que la especificación fue aprobada por el usuario ni que se ejecutaron pruebas.
