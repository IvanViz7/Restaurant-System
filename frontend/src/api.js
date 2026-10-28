const CLAVE = "sesion";
export const sesion = () => { try { return JSON.parse(localStorage.getItem(CLAVE)); } catch { return null; } };
export const guardarSesion = (s) => localStorage.setItem(CLAVE, JSON.stringify(s));
export const salir = () => { localStorage.removeItem(CLAVE); location.reload(); };
export const dinero = (n) => Number(n || 0).toLocaleString("es-MX", { style: "currency", currency: "MXN" });

export async function api(ruta, { metodo = "GET", cuerpo } = {}) {
  const s = sesion();
  const r = await fetch("/api" + ruta, {
    method: metodo,
    headers: { "Content-Type": "application/json", ...(s ? { Authorization: "Bearer " + s.token } : {}) },
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  if (r.status === 401 && s) salir();
  if (!r.ok) {
    const e = await r.json().catch(() => ({}));
    throw new Error(typeof e.detail === "string" ? e.detail : "Error " + r.status);
  }
  return r.json();
}
