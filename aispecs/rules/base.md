---
description: "Reglas generales del sistema Restaurante. Usa estas reglas junto con el contexto del proyecto y las reglas específicas del área."
alwaysApply: true
---

# Reglas generales del proyecto

## Contexto y fuentes de verdad

- Antes de cualquier tarea, lee `aispecs/AGENTS.md` y sigue sus indicaciones.
- Consulta [project-context.md](./project-context.md) para el resumen actual de arquitectura, rutas y comandos.
- Stack confirmado: FastAPI y Python 3.12; React 18, Vite 5 y JavaScript; PostgreSQL 16; SQLAlchemy 2 y psycopg 3; Docker Compose y Caddy.
- El código y la configuración vigentes son la fuente de verdad para detalles de implementación. No copies como hechos del proyecto ejemplos de otros repositorios.
- Las reglas específicas por área complementan estas reglas. Si hay una discrepancia, no inventes un comportamiento: verifica el código y actualiza la documentación relevante.

## Principios de trabajo

- Lee el código y la documentación relacionada antes de modificar.
- Haz cambios acotados al objetivo; no refactorices ni alteres datos ajenos a la tarea.
- Sigue los patrones existentes y conserva los contratos API que consume el frontend.
- Expón errores; no los conviertas en respuestas exitosas ni los ocultes con valores predeterminados.
- Valida los cambios con el comando existente más pequeño que cubra el comportamiento afectado.
- No versionar `.env`, credenciales, secretos ni contenido generado en `respaldos/`.

## Convenciones de nombres

| Ámbito | Convención | Ejemplo |
|---|---|---|
| Dominio y API | Español, conserva términos existentes | `Pedido`, `Sucursal`, `/pedidos` |
| Python: módulos, funciones y variables | `snake_case` | `migraciones.py`, `sucursal_activa` |
| Python: clases | `PascalCase` | `PedidoItem` |
| Python: constantes | `UPPER_SNAKE_CASE` | `TABLAS_RLS` |
| SQL: tablas y columnas | `snake_case`; tablas en plural | `pedido_items`, `organizacion_id` |
| React: componentes | `PascalCase` | `Dashboard` |
| JavaScript: funciones, variables y hooks | `camelCase` | `guardarSesion` |
| CSS | Minúsculas con guiones | `.usuario-form` |

## Reglas críticas compartidas

- El backend es la autoridad para autenticar, autorizar y validar recursos. La navegación del frontend no es un control de seguridad.
- Toda operación debe respetar el aislamiento por organización y, cuando aplique, por sucursal. Preserva las políticas RLS y el rol de aplicación `app`.
- Conserva los roles existentes (`dueno`, `gerente`, `mesero`, `cocinero`, `cajero`) y sus permisos del servidor.
- Conserva el precio y costo históricos de los pedidos y la consistencia transaccional entre pedidos e inventario.
- Los cambios de esquema requieren una nueva migración versionada; no edites migraciones aplicadas ni uses `create_all()` como sustituto.
- No registres ni documentes contraseñas, tokens, secretos ni credenciales.
- Al cambiar rutas, permisos, contratos, roles o flujos, actualiza ambos lados de la API y su documentación funcional.

## Reglas por área

- [backend-standards.md](./backend-standards.md): API, autenticación, sesiones, transacciones y backend.
- [database-standards.md](./database-standards.md): modelos, PostgreSQL, RLS, precisión y migraciones.
- [frontend-standards.md](./frontend-standards.md): React, Vite, API, sesión y estilos.
- [sync-pipeline-standards.md](./sync-pipeline-standards.md): alcance de los procesos de migración, respaldo y cualquier futura sincronización.
