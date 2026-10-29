---
description: "Estándares para la interfaz de Restaurante: React 18, Vite 5, JavaScript, llamadas API, sesión y PWA."
globs: ["frontend/src/**/*.js", "frontend/src/**/*.jsx", "frontend/src/**/*.css", "frontend/**/*.html", "frontend/package.json", "frontend/vite.config.js"]
alwaysApply: true
---

# Estándares de frontend — React 18 y Vite 5

## Stack y estructura

| Componente | Tecnología | Fuente |
|---|---|---|
| UI | React 18.3 | `frontend/package.json` |
| Build y desarrollo | Vite 5.4 | `frontend/package.json`, `frontend/vite.config.js` |
| Lenguaje | JavaScript ES modules con JSX | `frontend/src/` |
| Iconos | Lucide React | `frontend/src/App.jsx` |
| Producción | Nginx en imagen `nginx:alpine` | `frontend/Dockerfile` |
| Aplicación instalable | Service worker | `frontend/src/main.jsx`, `frontend/public/sw.js` |

La aplicación es compacta y está organizada en `App.jsx`, `api.js`, `estilos.css` y `main.jsx`. Sigue la estructura existente; no migres a TypeScript ni agregues bibliotecas sin una necesidad concreta.

## Componentes y estilos

- Componentes React en `PascalCase`; funciones, variables y hooks en `camelCase`; constantes globales en `UPPER_SNAKE_CASE`.
- Usa componentes funcionales y hooks de React siguiendo los patrones existentes.
- Mantén estilos en `frontend/src/estilos.css`, con clases descriptivas en minúsculas y guiones.
- Conserva el diseño adaptable para pantallas pequeñas y respeta las preferencias de movimiento reducido cuando se agreguen animaciones.
- Usa `lucide-react` para iconos ya disponibles en el proyecto; no agregues paquetes de iconos duplicados.

## API, sesión y errores

- Centraliza peticiones HTTP, token, cierre de sesión y formato de errores en `frontend/src/api.js`; usa `api()` desde los componentes.
- Las rutas del cliente se pasan relativas a `/api` (por ejemplo, `api("/pedidos")`). No codifiques hosts ni puertos en la interfaz.
- Las llamadas autenticadas agregan `Authorization: Bearer <token>` desde la sesión. Conserva el cierre de sesión ante un `401`.
- Muestra errores de API al usuario; no conviertas una petición fallida en éxito ni descartes silenciosamente errores funcionales.
- Conserva el contrato JSON, nombres de campos, códigos de estado y permisos implementados por el backend. Si cambia un contrato, actualiza ambos lados.
- La sesión actual se guarda en `localStorage` bajo la clave `sesion`. No almacenes ahí contraseñas ni secretos adicionales.
- La interfaz puede ocultar acciones según el rol para mejorar la experiencia, pero el backend siempre debe volver a validar permisos.

## Roles y flujos

Los roles son `dueno`, `gerente`, `mesero`, `cocinero` y `cajero`. Usa los permisos descritos por el backend: el cocinero consulta cocina en modo de solo lectura; el cajero puede consultar y cobrar, pero no crear ni modificar pedidos; el mesero gestiona pedidos conforme a las restricciones de preparación y cobro.

La cocina recibe actualizaciones por WebSocket en `/api/ws/cocina`; preserva la conexión y el formato de autenticación actuales al modificar ese flujo.

## Desarrollo y validación

Desde `frontend/`:

```bash
npm ci
npm run dev
npm run build
```

Vite sirve el frontend y usa el proxy de desarrollo existente para `/api` y WebSocket hacia `http://localhost:8000`. En Compose, el acceso integrado es `http://localhost:5600`; Caddy enruta `/api/*` al backend y las demás rutas al frontend.

Ejecuta `npm run build` para validar cambios que afecten el frontend. No asumas un runner de pruebas unitarias: `package.json` actualmente define `dev` y `build`.
