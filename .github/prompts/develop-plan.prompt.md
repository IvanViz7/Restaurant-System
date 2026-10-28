---
description: "Implementa el plan de desarrollo seleccionado fase por fase, verifica cada cambio y mantiene actualizado su checklist."
name: "Develop Plan"
argument-hint: "<ruta del plan> o <historia/ticket> <database|backend|frontend>"
---

Implementa el plan de desarrollo indicado aquí: `${input:target: ruta del plan o historia/ticket y capa}`.

Si el mensaje que acompaña a este prompt ya identifica claramente un plan, úsalo y no vuelvas a solicitarlo.

## Reglas del repositorio

- Antes de empezar, lee íntegramente `aispecs/AGENTS.md` y sigue sus indicaciones.
- Lee `aispecs/rules/base.md` y las instrucciones adicionales aplicables. No inventes reglas específicas de capa si no existen.
- Usa `Documentacion/UserStories/` para documentación de historias; no crees una carpeta duplicada `Documentación/`.
- Respeta el stack actual: Python 3.12, FastAPI, SQLAlchemy 2, PostgreSQL 16, React 18, JavaScript, Vite y Docker Compose.
- Conserva los cambios existentes del usuario. Antes de editar un archivo, revisa su contenido y los cambios del worktree; integra los cambios relacionados y no reviertas ni sobrescribas trabajo ajeno.
- No despliegues, no ejecutes migraciones contra una base de datos persistente, no hagas commit, push ni abras PR. No agregues dependencias salvo que el cambio requerido y el fallo de una validación demuestren que son necesarias.

## Paso 1: Identificar el plan

Se puede especificar una ruta a un plan o una historia/ticket y una capa:

| Formato | Ejemplo |
|---|---|
| `<ruta del plan>` | `Documentacion/UserStories/.../Plan-T-00001-backend.md` |
| `<historia> <capa>` | `00001 backend`, `00001 db`, `00001 fe` |
| `<ticket> <capa>` | `T-00001 backend` |

Capas aceptadas: `database`/`db`, `backend`/`be`, `frontend`/`fe`.

1. Los planes de tickets agrupados siguen el patrón `Documentacion/UserStories/<historia>/Plan-T-<ticket>-<capa>.md`; puede haber también planes generales de historia con otro nombre.
2. Si se indicó una ruta, confirma que existe y que es un plan con checklist. Si se indicó historia/ticket y capa, busca los planes coincidentes bajo `Documentacion/UserStories/`.
3. Si no hay coincidencias, muestra las rutas candidatas disponibles o el error de ruta. Si hay más de un plan posible, pide al usuario que elija. No ejecutes todos los planes de una historia implícitamente.
4. Lee el plan completo, el ticket fuente que cita, la historia y los documentos técnicos directamente relacionados. Confirma la capa y alcance antes de modificar código.
5. Si el plan o su ticket de origen no permiten determinar requisitos importantes, o hay decisiones incompatibles/ambiguas de seguridad, permisos, datos o producto, detente y solicita aclaración antes de implementar ese trabajo.

## Paso 2: Comprobar el estado del plan y del repositorio

- Inspecciona `git status` y el diff de los archivos que planeas tocar. No limpies el worktree ni restaures archivos.
- Cuenta las casillas `- [ ]` y `- [x]` y comprueba el `progress` del frontmatter.
- Si no quedan tareas sin marcar, informa que el plan ya está completo y detente; no repitas cambios.
- Si el conteo del frontmatter no coincide con las casillas, corrige el conteo para reflejar el estado real al actualizar el plan; no marques tareas solo para que coincida.
- Revisa los archivos relevantes, patrones existentes y pruebas disponibles antes de editar. En backend, inspecciona rutas, dependencias, modelos y migraciones pertinentes; en frontend, inspecciona componentes, API y estilos relacionados.
- Convierte mentalmente las fases y tareas del plan en una secuencia de trabajo. Sigue su orden; si una tarea es obsoleta, insegura, incompatible con el ticket o técnicamente innecesaria, no la ejecutes a ciegas: explica el motivo y detente para acordar el ajuste.

## Paso 3: Implementar fase por fase

Trabaja en orden y no empieces una fase nueva hasta cerrar o bloquear la fase actual:

1. Selecciona la siguiente tarea `- [ ]` de la primera fase incompleta.
2. Implementa el cambio completo y quirúrgico, siguiendo patrones del repositorio y respetando todo el alcance y las reglas de seguridad.
3. Ejecuta las validaciones focalizadas que cubran el requisito implementado. Inspecciona el resultado; no des por válido un comando que no corrió o no verificó el comportamiento.
4. Marca una tarea como `- [x]` únicamente cuando su condición de terminado esté comprobada. Una tarea bloqueada, no verificada o pendiente de decisión permanece sin marcar; reporta el bloqueo en el plan sin atribuirse trabajo no realizado.
5. Al terminar la fase, actualiza el archivo de plan en una edición enfocada: conserva las notas y el estado preexistentes, marca solo trabajo completado y calcula `progress` usando el número exacto de casillas completadas y el total de casillas. No cambies otros archivos de planificación.
6. Continúa con la fase siguiente solo si todas las tareas de la fase actual están completadas. Si una verificación falla, intenta una corrección razonable dentro del alcance; si no se resuelve de forma segura, deja el trabajo verificable registrado y detente con el bloqueo explícito.

No edites el plan para “hacerlo coincidir” con una implementación incompleta. Si una tarea agrupa varias acciones, déjala sin marcar hasta verificar todas; divide la tarea solo si es necesario, conserva el significado del plan y actualiza el total de progreso con precisión.

## Reglas de implementación por capa

### Todas las capas

- Mantén los nombres del dominio en español como el código existente; conserva contratos de API y formatos de datos salvo que el ticket exija cambiarlos.
- Mantén cambios enfocados, tipados cuando aplique, y consistentes con helpers, patrones y dependencias ya presentes.
- Expón errores de forma clara; no uses fallbacks silenciosos ni captures excepciones ampliamente para ocultar fallos.
- No incluyas secretos, tokens ni credenciales en código, documentación, pruebas o logs.
- Actualiza documentación funcional/técnica directamente relacionada cuando cambien contratos, permisos o flujos.

### Database

- PostgreSQL y SQLAlchemy son el patrón del proyecto. Los modelos están en `backend/app/modelos.py`; las migraciones versionadas están en `backend/app/migraciones.py`.
- Para cambios en tablas existentes, crea una nueva migración idempotente y compatible con datos existentes; `Base.metadata.create_all()` no sustituye migraciones.
- Conserva Row Level Security y el aislamiento por `organizacion_id`; no uses rol superusuario para evitar restricciones.
- No ejecutes una migración sobre una base de datos persistente o compartida. Verifica código y, solo si hay una base temporal/aislada disponible y apropiada, solicita confirmación antes de ejecutar cambios de esquema.
- Verifica la migración y el modelo con las herramientas disponibles; no inventes scripts SQL independientes ni un framework de migraciones no instalado.

### Backend

- Implementa la API con FastAPI, SQLAlchemy 2 y los modelos Pydantic existentes; reutiliza las dependencias de sesión, autenticación y permisos.
- La autorización se valida en el servidor, junto con organización y sucursal. Filtrar la interfaz no sustituye estos controles.
- Usa consultas parametrizadas. Conserva transacciones y restricciones RLS. En dinero/cantidades utiliza `Decimal` y `Numeric` cuando corresponda.
- Para cambios de pedidos/inventario, conserva el historial de precio/costo y el registro/restauración transaccional del consumo; no permitas modificar pedidos cobrados o cuya preparación comenzó.
- Ejecuta pruebas persistentes existentes si las hay. Si no existen pruebas relevantes, verifica con los comandos disponibles y describe claramente la cobertura que falta; no afirmes pruebas manuales que no realizaste.

### Frontend

- Implementa la interfaz con React y JavaScript, respetando la estructura actual. Centraliza las llamadas HTTP y manejo de sesión/errores en `frontend/src/api.js`.
- Respeta permisos de navegación y acciones por rol, pero no los trates como control de seguridad.
- Maneja errores y estados de interfaz de forma coherente con los componentes existentes; conserva los datos ingresados ante fallos cuando corresponda.
- Verifica los cambios con `npm run build` en `frontend/` y con pruebas focalizadas si existen.

## Paso 4: Verificación final

Al completar todas las fases:

- Recorre los criterios de aceptación y verifica cada uno con pruebas, build u otra evidencia observable apropiada. Informa los criterios que no pudiste verificar.
- Ejecuta las validaciones mínimas relevantes para los archivos cambiados. Si una validación falla por entorno/dependencias o no puede ejecutarse, informa el comando y el motivo; no reportes éxito.
- Revisa el diff final para detectar cambios no relacionados, errores, secretos accidentales y modificaciones no intencionadas del plan.
- Confirma que `progress` y las casillas coinciden. El plan solo se considera completo si no queda ninguna tarea `- [ ]`.
- No modifiques el plan para añadir nuevas tareas durante el cierre sin explicar el cambio y actualizar correctamente el total.

## Paso 5: Reportar resultado

Resume:

- Plan, ticket y capa trabajados.
- Progreso final `N / N` o progreso parcial exacto.
- Archivos creados y modificados, con breve descripción.
- Validaciones ejecutadas y su resultado.
- Tareas pendientes, bloqueos y criterios que no se pudieron verificar.

Si el plan quedó parcial, identifica la siguiente tarea sin marcar y no declares la implementación completa.
