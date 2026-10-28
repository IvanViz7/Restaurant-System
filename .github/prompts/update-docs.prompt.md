---
description: "Actualiza la documentación directamente afectada por cambios confirmados en código, datos, configuración o arquitectura."
name: "Update Documentation"
argument-hint: "<describe el cambio realizado o indica sus archivos>"
---

Actualiza la documentación pertinente a estos cambios: `${input:changes:describe el cambio realizado o indica sus archivos}`.

Si el mensaje que acompaña a este prompt describe claramente los cambios, úsalo y no vuelvas a solicitar esa información.

## Reglas del repositorio

- Antes de empezar, lee íntegramente `aispecs/AGENTS.md` y aplica sus indicaciones.
- Usa `Documentacion/` (sin acento) para la documentación funcional existente; no crees un duplicado `Documentación/`.
- Mantén las reglas de agente en `aispecs/AGENTS.md`, las reglas generales en `aispecs/rules/` y los prompts de Copilot en `.github/prompts/`, cada uno en su ubicación correspondiente.
- Respeta el stack real: FastAPI, SQLAlchemy, PostgreSQL, React, JavaScript, Vite y Docker Compose. No documentes tecnologías, versiones, servicios, endpoints ni convenciones no confirmados.
- Este prompt actualiza documentación, no implementa código ni realiza despliegues o migraciones.

## Paso 1: Entender los cambios confirmados

1. Identifica si los cambios ya están presentes en el código/configuración, si el usuario solo los describe, o si todavía no se han realizado. Inspecciona el diff y los archivos relevantes cuando existan.
2. Si el alcance no puede determinarse o hay discrepancias entre la descripción y el código, pide aclaración. No documentes como hecho un cambio planeado o fallido.
3. Inspecciona el estado del worktree antes de editar; integra cambios del usuario y no los reviertas.
4. Determina el tipo de cambio y los documentos que realmente existen y deben mantenerse sincronizados:

| Cambio confirmado | Documentación a considerar |
|---|---|
| Arquitectura, stack o topología de servicios | `aispecs/AGENTS.md`, `aispecs/README.md`, `docker-compose.yml`, `proxy/Caddyfile` y documentación de arquitectura existente |
| API, autenticación, permisos o flujo de usuario | Documentación funcional de la historia/tickets en `Documentacion/UserStories/`; `aispecs/AGENTS.md` si cambian decisiones generales |
| Tabla, columna o migración | Documentación técnica existente de la historia y guía del proyecto; reflejar nombres reales de `backend/app/modelos.py` y `backend/app/migraciones.py` |
| Interfaz o flujo de frontend | Documentación funcional relacionada y `aispecs/README.md` solo si cambia una instrucción estructural o de arquitectura |
| Reglas de desarrollo o personalización de agente | El archivo correspondiente en `aispecs/rules/`, `aispecs/AGENTS.md` o `.github/`, según el alcance |
| Incidente o solución operativa reutilizable | Documentación de operación existente, si la hay; no crear un sistema de troubleshooting genérico sin necesidad |

Esta tabla orienta la búsqueda, no obliga a modificar todos los archivos listados. Inspecciona y actualiza solo documentos pertinentes. No asumas que existe `Documentacion/README.md`, un índice maestro, reglas por capa ni una tabla de punteros; usa únicamente los archivos que encuentres.

## Paso 2: Elegir el alcance documental

- Actualiza el documento más cercano al comportamiento cambiado; evita duplicar información entre AGENTS, README, reglas y documentación de historia.
- Cambios de producto o criterios de aceptación van junto a la historia correspondiente. No sobrescribas el texto `## [original]` de una historia enriquecida. Actualiza únicamente la sección enriquecida cuando sea claramente identificable.
- Si se requiere modificar un archivo de tickets o plan, conserva IDs, estado, progreso y notas existentes; cambia solo lo que quede invalidado por el trabajo y mantén la trazabilidad.
- No crees archivos índice, guías, secciones de versión, fechas o estados del proyecto si el repositorio no usa ese patrón o el cambio no los necesita.
- Si no existe un documento apropiado, crea uno solo cuando aporte una referencia duradera necesaria; enlázalo desde la guía apropiada si corresponde. Si la ubicación o decisión de documentación es ambigua, pregunta antes de crear.

## Paso 3: Actualizar con precisión

- Escribe en español y sigue el tono, formato y nivel de detalle del documento existente.
- Documenta el comportamiento vigente, contratos confirmados, pasos de uso/operación necesarios y restricciones relevantes. Para una API, incluye método, ruta y solicitud/respuesta solo si están confirmados.
- Para cambios de esquema, documenta migración versionada e idempotente en `backend/app/migraciones.py` y cualquier compatibilidad importante; no describas `create_all()` como migración.
- Para cambios de autorización, deja claro que backend valida roles, organización y sucursal; la interfaz no es una barrera de seguridad.
- Para cambios de pedidos o inventario, preserva la explicación del historial de precios/costos y del registro/restauración transaccional del consumo cuando aplique.
- No incluyas secretos, tokens, contraseñas, datos personales ni contenido de respaldos. No versionar ni documentar valores de `.env`.
- No presentes preguntas abiertas, propuestas o validaciones no ejecutadas como decisiones o resultados confirmados.
- Mantén los cambios quirúrgicos y no reescribas documentos completos para modificar un detalle pequeño.

## Paso 4: Verificar consistencia

Antes de terminar:

- Confirma que cada afirmación nueva corresponde al código, configuración o decisión proporcionada.
- Revisa enlaces relativos, nombres de rutas y archivos citados.
- Busca contradicciones con `aispecs/AGENTS.md`, `aispecs/README.md` y la documentación funcional directamente relacionada; actualiza solo lo necesario.
- Revisa el diff para confirmar que no cambiaste código, historias originales ni documentación no relacionada.
- No afirmes sincronización con índices/archivos que no existen.

## Paso 5: Confirmar

Informa los archivos documentales actualizados, el resumen de cada cambio y cualquier archivo relacionado que no se pudo actualizar (con la razón). Si no era necesaria una modificación documental, explica brevemente por qué. No reportes pruebas como ejecutadas, salvo que efectivamente las hayas corrido.
