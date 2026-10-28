# Reglas base del proyecto

Aplican a todos los cambios. Si una regla específica del área es más estricta, prevalece esa regla.

## Convenciones de naming

- Mantén los nombres del dominio en español, como en el código existente (`Pedido`, `Sucursal`, `sucursal_id` y `/pedidos`).
- Python: módulos y funciones en `snake_case`; clases en `PascalCase`; constantes globales en `MAYUSCULAS_CON_GUIONES`.
- SQLAlchemy: modelos en `PascalCase`, tablas en plural `snake_case` y columnas en `snake_case`.
- React/JavaScript: componentes en `PascalCase`; funciones, variables y hooks en `camelCase`; constantes compartidas en `MAYUSCULAS_CON_GUIONES`.
- CSS: usa clases descriptivas en minúsculas con guiones, siguiendo nombres como `.usuario-form` y `.barra-op`.
- Conserva los nombres de rutas, campos JSON y roles que ya consume el frontend. Si cambia un contrato, actualiza ambos lados y la documentación funcional.

## Patrones del proyecto

- Backend: expón la API con FastAPI en `backend/app/main.py`; define entradas con modelos Pydantic y usa dependencias compartidas para autenticación, permisos y sesión de base de datos.
- Persistencia: declara modelos y tipos reutilizables en `backend/app/modelos.py`. Usa SQLAlchemy 2 y consultas parametrizadas; no construyas SQL con datos de entrada.
- Frontend: mantén la interfaz en React y centraliza las llamadas HTTP, la sesión y el manejo de errores en `frontend/src/api.js`.
- Mantén la solución dentro del stack actual (FastAPI, SQLAlchemy, PostgreSQL, React y Vite). No agregues dependencias para resolver algo que el stack ya cubre.
- Para errores de API, devuelve el estado y mensaje apropiados con `HTTPException`; en la interfaz, muestra el error recibido en vez de ocultarlo o convertirlo en éxito.

## Reglas críticas

### Seguridad, organización y sucursal

- El backend es la autoridad para autenticar y autorizar. Ocultar secciones o botones en React mejora la UX, pero nunca sustituye `Depends(solo(...))` ni las comprobaciones del servidor.
- Toda consulta o escritura operativa debe quedar limitada a la organización autenticada. Conserva `organizacion_id`, el contexto `app.org_id` de la sesión y las políticas RLS; no conectes la aplicación como superusuario ni desactives RLS para resolver un flujo.
- Respeta el aislamiento de sucursal: dueño y gerente pueden elegirla donde corresponde; mesero, cocinero y cajero operan únicamente en la sucursal asignada. Valida en el backend la pertenencia de mesas, pedidos e identificadores recibidos.
- Mantén las contraseñas con hash y verifica el JWT en el servidor. No registres ni incluyas contraseñas, tokens, secretos o credenciales en código, documentación, logs o pruebas.

### Datos, dinero e inventario

- Todo cambio de esquema existente requiere una nueva versión en `backend/app/migraciones.py`, idempotente y compatible con los datos actuales. `Base.metadata.create_all()` no sustituye una migración.
- Conserva precisión monetaria y de cantidades con `Decimal` y los tipos `Numeric` del modelo; evita cálculos persistentes con `float`.
- Los ítems de pedido deben conservar el precio y costo unitarios históricos. No recalcules ventas pasadas desde los precios o costos actuales del menú o de los insumos.
- El consumo de recetas y el inventario deben cambiar en la misma transacción que el pedido. Al editar o eliminar un pedido, restaura el consumo registrado antes de volver a aplicarlo o borrar sus ítems; nunca ajustes stock de forma parcial.
- No permitas editar ni eliminar pedidos cobrados o cuya preparación haya comenzado. Conserva también la validación del servidor aunque la interfaz oculte esas acciones.

### Cambios funcionales

- Conserva los roles existentes (`dueno`, `gerente`, `mesero`, `cocinero`, `cajero`) y aplica permisos por operación; el cocinero es de solo lectura y el cajero consulta y cobra, sin crear ni modificar pedidos.
- Al cambiar contratos, permisos, flujos, roles o comportamiento de pedidos/inventario, actualiza la documentación relevante y verifica los casos afectados.
- No sobrescribas datos de usuarios ni respaldos como parte de una tarea rutinaria. No versionar secretos, `.env` ni el contenido generado en `respaldos/`.
