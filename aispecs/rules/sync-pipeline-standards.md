---
description: "Estándares para procesos de datos de Restaurante: distinguir migraciones, respaldos y futuras sincronizaciones; conservar transacciones e aislamiento."
globs: ["backend/app/migraciones.py", "docker-compose.yml", "db/**"]
alwaysApply: true
---

# Estándares de procesos y sincronización de datos

## Alcance actual

Este repositorio no contiene actualmente un pipeline de sincronización de datos de terceros, tareas ETL, workers de sincronización ni multiprocessing. No agregues dependencias, servicios, fuentes externas o supuestos de sincronización basados en ejemplos de otros proyectos.

Los procesos existentes son distintos y no deben confundirse:

1. **Migraciones de esquema:** `backend/app/migraciones.py` se ejecuta durante el arranque de FastAPI. Usa transacción, bloqueo asesor y versiones registradas en `schema_migrations`.
2. **Respaldos:** el servicio `respaldos` de Compose ejecuta diariamente `pg_dump` de `restaurante`, comprime el resultado en `./respaldos` y elimina respaldos con más de 14 días. Es una copia de seguridad, no una sincronización ni una réplica.
3. **Perfil IA:** el perfil `ia` inicia Ollama; no importa, transforma ni sincroniza datos.

## Reglas para los procesos existentes

- Los cambios de esquema van en migraciones nuevas y compatibles con datos existentes; no edites migraciones aplicadas.
- Mantén la consistencia de cada cambio dentro de una transacción y respeta el rol `app`, RLS y `app.org_id` para operaciones de la aplicación.
- El contenedor de respaldos usa credenciales de administración en su entorno. No expongas valores de secretos, no los copies a logs o documentación y no uses ese rol desde las rutas de la aplicación.
- No sobrescribas, elimines ni versionas respaldos como efecto incidental de una tarea de desarrollo.
- Si falla un proceso de migración o respaldo, conserva evidencia del fallo y comunícalo; no lo reportes como exitoso ni lo ocultes.

## Requisitos para una futura sincronización

Antes de implementar una sincronización real, identifica y documenta su origen, destino, propietario funcional, frecuencia, política de reintentos, tratamiento de borrados, manejo de datos sensibles y estrategia de recuperación. No inventes esos requisitos.

Cuando exista un requerimiento aprobado:

- Diseña la operación para ser idempotente y segura ante reintentos; define una clave de deduplicación o una regla de upsert explícita.
- Valida y limita cada escritura por organización y, cuando aplique, sucursal. Nunca permitas que datos de una organización sobrescriban los de otra.
- Agrupa las escrituras relacionadas en transacciones; define explícitamente qué ocurre si un lote falla parcialmente.
- Registra inicio, resultado, cantidades y errores sin incluir contraseñas, tokens, datos personales innecesarios ni secretos.
- Usa límites, control de concurrencia y reintentos acotados con backoff para no saturar PostgreSQL ni servicios externos.
- Añade pruebas de duplicados, reintentos, fallos parciales, aislamiento y recuperación antes de habilitar el proceso automáticamente.
- Añade un servicio o scheduler a Compose solo cuando el requerimiento y su ciclo de vida estén definidos; documenta activación, observabilidad, pausa y recuperación.

No uses borrado físico, sincronización bidireccional ni resolución automática de conflictos sin una decisión explícita del producto.
