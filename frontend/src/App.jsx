import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { api, dinero, guardarSesion, salir, sesion } from "./api";

/* ---------- acceso ---------- */
function Acceso({ alEntrar }) {
  const [nuevo, setNuevo] = useState(false);
  const [f, setF] = useState({});
  const [error, setError] = useState("");
  const campo = (k, ph, tipo = "text") => (
    <input placeholder={ph} type={tipo} value={f[k] || ""} onChange={(e) => setF({ ...f, [k]: e.target.value })} />
  );
  const enviar = async () => {
    const cuerpo = nuevo ? f : {
      codigo_restaurante: f.codigo_restaurante, usuario: f.usuario, clave: f.clave,
    };
    try { alEntrar(await api(nuevo ? "/auth/registro" : "/auth/login", { metodo: "POST", cuerpo })); }
    catch (e) { setError(e.message); }
  };
  return (
    <div className="acceso">
      <h1>{nuevo ? "Crea tu restaurante" : "Entrar"}</h1>
      {nuevo && campo("organizacion", "Nombre del restaurante")}
      {nuevo && campo("sucursal", "Nombre de la primera sucursal")}
      {nuevo && campo("nombre", "Tu nombre")}
      {!nuevo && campo("codigo_restaurante", "Código del restaurante")}
      {nuevo ? campo("email", "Correo", "email") : campo("usuario", "Usuario o correo")}
      {campo("clave", "Contraseña", "password")}
      {error && <p className="error">{error}</p>}
      <button className="primario" onClick={enviar}>{nuevo ? "Crear cuenta" : "Entrar"}</button>
      <button className="texto" onClick={() => { setNuevo(!nuevo); setError(""); }}>
        {nuevo ? "Ya tengo cuenta" : "Registrar mi restaurante"}
      </button>
    </div>
  );
}

/* ---------- usuarios ---------- */
function Usuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [sucursales, setSucursales] = useState([]);
  const [f, setF] = useState({ rol: "mesero" });
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const requiereSucursal = ["mesero", "cocinero", "cajero"].includes(f.rol);
  const cargar = async () => {
    try {
      const [us, sucs] = await Promise.all([api("/usuarios"), api("/sucursales")]);
      setUsuarios(us);
      setSucursales(sucs);
    } catch (e) { setError(e.message); }
  };
  useEffect(() => { cargar(); }, []);
  const crear = async (e) => {
    e.preventDefault();
    setError(""); setMensaje("");
    try {
      await api("/usuarios", { metodo: "POST", cuerpo: {
        ...f, usuario: f.usuario.trim().toLowerCase(), sucursal_id: f.sucursal_id ? Number(f.sucursal_id) : null,
      } });
      setF({ rol: "mesero" });
      setMensaje("Usuario creado.");
      await cargar();
    } catch (err) { setError(err.message); }
  };
  const nombres = { dueno: "Dueño", gerente: "Gerente", mesero: "Mesero", cocinero: "Cocinero", cajero: "Cajero" };
  return (
    <>
      <section>
        <h2>Crear usuario</h2>
        <form className="usuario-form" onSubmit={crear}>
          <label>Nombre<input required value={f.nombre || ""} onChange={(e) => setF({ ...f, nombre: e.target.value })} /></label>
          <label>Usuario<input required minLength="3" maxLength="32" pattern="[a-zA-Z0-9._-]+" autoComplete="username" value={f.usuario || ""} onChange={(e) => setF({ ...f, usuario: e.target.value })} /></label>
          <label>Contraseña inicial<input required type="password" autoComplete="new-password" value={f.clave || ""} onChange={(e) => setF({ ...f, clave: e.target.value })} /></label>
          <label>Rol<select value={f.rol} onChange={(e) => setF({ ...f, rol: e.target.value, sucursal_id: "" })}>
            <option value="gerente">Gerente</option><option value="mesero">Mesero</option>
            <option value="cocinero">Cocinero</option><option value="cajero">Cajero</option>
          </select></label>
          <label>Sucursal<select required={requiereSucursal} value={f.sucursal_id || ""} onChange={(e) => setF({ ...f, sucursal_id: e.target.value })}>
            <option value="">{requiereSucursal ? "Selecciona una sucursal" : "Todas las sucursales"}</option>
            {sucursales.map((suc) => <option key={suc.id} value={suc.id}>{suc.nombre}</option>)}
          </select></label>
          {error && <p className="error">{error}</p>}
          {mensaje && <p className="correcto">{mensaje}</p>}
          <button className="primario" type="submit">Crear usuario</button>
        </form>
      </section>
      <section>
        <h2>Usuarios del restaurante</h2>
        {usuarios.length === 0 ? <p className="vacio">No hay usuarios.</p> : usuarios.map((u) => (
          <div className="tarjeta" key={u.id}>
            <div className="fila"><b>{u.nombre}</b><span>{nombres[u.rol] || u.rol}</span></div>
            <small>{u.usuario || u.email} · {sucursales.find((suc) => suc.id === u.sucursal_id)?.nombre || "Todas las sucursales"}</small>
          </div>
        ))}
      </section>
    </>
  );
}

/* ---------- dashboard ---------- */
function Ranking({ titulo, datos, orden }) {
  const orde = [...datos].sort((a, b) => b[orden] - a[orden]);
  const top = orde.slice(0, 5);
  const bajo = orde.length > 5 ? orde.slice(-5).reverse() : [];
  const max = Math.max(1, ...top.map((d) => d[orden]));
  const Fila = ({ d }) => (
    <li>
      <div className="fila"><span>{d.nombre}</span><b>{orden === "unidades" ? d.unidades : dinero(d[orden])}</b></div>
      <div className="barra"><i style={{ width: (Math.max(0, d[orden]) / max) * 100 + "%" }} /></div>
      <small>{d.unidades} vendidos · {dinero(d.ingresos)} · margen {d.margen_pct}%</small>
    </li>
  );
  return (
    <section>
      <h2>{titulo}</h2>
      {datos.length === 0 ? <p className="vacio">Aún no hay platillos. Créalos en Menú.</p> : (
        <>
          <h3>Más vendidos</h3><ul>{top.map((d) => <Fila key={d.id} d={d} />)}</ul>
          {bajo.length > 0 && <><h3>Menos vendidos</h3><ul>{bajo.map((d) => <Fila key={d.id} d={d} />)}</ul></>}
        </>
      )}
    </section>
  );
}

function Dashboard() {
  const [dias, setDias] = useState(30);
  const [orden, setOrden] = useState("unidades");
  const [r, setR] = useState(null);
  const [p, setP] = useState([]);
  useEffect(() => {
    api(`/metricas/resumen?dias=${dias}`).then(setR);
    api(`/metricas/platillos?dias=${dias}`).then(setP);
  }, [dias]);
  const Kpi = ({ t, v }) => <div className="kpi"><small>{t}</small><b>{v}</b></div>;
  return (
    <>
      <div className="barra-op">
        <select value={dias} onChange={(e) => setDias(+e.target.value)}>
          <option value={1}>Hoy</option><option value={7}>7 días</option><option value={30}>30 días</option><option value={90}>90 días</option>
        </select>
        <select value={orden} onChange={(e) => setOrden(e.target.value)}>
          <option value="unidades">Ordenar por unidades</option><option value="ingresos">Ordenar por venta bruta</option><option value="utilidad">Ordenar por utilidad</option>
        </select>
      </div>
      {r && (
        <div className="kpis">
          <Kpi t="Ventas" v={dinero(r.ventas)} />
          <Kpi t="Utilidad estimada" v={dinero(r.utilidad)} />
          <Kpi t="Food cost" v={r.food_cost_pct + "%"} />
          <Kpi t="Ticket promedio" v={dinero(r.ticket_promedio)} />
          <Kpi t="Propinas" v={dinero(r.propinas)} />
          <Kpi t="Vs. periodo anterior" v={r.variacion_pct == null ? "—" : (r.variacion_pct > 0 ? "+" : "") + r.variacion_pct + "%"} />
        </div>
      )}
      <Ranking titulo="Platillos" datos={p.filter((x) => x.tipo === "comida")} orden={orden} />
      <Ranking titulo="Bebidas" datos={p.filter((x) => x.tipo === "bebida")} orden={orden} />
    </>
  );
}

/* ---------- pedidos ---------- */
function Pedidos() {
  const rol = sesion()?.usuario.rol;
  const puedeCrear = ["dueno", "gerente", "mesero"].includes(rol);
  const puedeCobrar = ["dueno", "gerente", "mesero", "cajero"].includes(rol);
  const [mesas, setMesas] = useState([]);
  const [menu, setMenu] = useState([]);
  const [abiertos, setAbiertos] = useState([]);
  const [mesa, setMesa] = useState("");
  const [carrito, setCarrito] = useState([]);
  const [error, setError] = useState("");
  const [editandoId, setEditandoId] = useState(null);
  const [confirmarEliminarId, setConfirmarEliminarId] = useState(null);
  const [cobroId, setCobroId] = useState(null);
  const [propina, setPropina] = useState("0");
  const [metodoPago, setMetodoPago] = useState("efectivo");
  const [errorCobro, setErrorCobro] = useState("");
  const [cobrando, setCobrando] = useState(false);
  const cargar = () => api("/pedidos").then(setAbiertos);
  useEffect(() => {
    if (puedeCrear) { api("/mesas").then(setMesas); api("/platillos").then(setMenu); }
    cargar();
  }, []);

  const agregar = (pl) => setCarrito((c) => {
    const i = c.findIndex((x) => x.platillo_id === pl.id);
    if (i >= 0) return c.map((x, j) => (j === i ? { ...x, cantidad: x.cantidad + 1 } : x));
    return [...c, { platillo_id: pl.id, nombre: pl.nombre, cantidad: 1, nota: "" }];
  });
  const nota = (i, v) => setCarrito((c) => c.map((x, j) => (j === i ? { ...x, nota: v } : x)));
  const quitar = (i) => setCarrito((c) => c.filter((_, j) => j !== i));
  const iniciarEdicion = (pedido) => {
    setEditandoId(pedido.id);
    setMesa(pedido.mesa_id ? String(pedido.mesa_id) : "");
    setCarrito(pedido.items.map((item) => ({
      platillo_id: item.platillo_id, nombre: item.nombre, cantidad: item.cantidad, nota: item.nota,
    })));
    setError("");
  };
  const cancelarEdicion = () => { setEditandoId(null); setMesa(""); setCarrito([]); setError(""); };
  const enviar = async () => {
    try {
      await api(editandoId ? `/pedidos/${editandoId}` : "/pedidos", {
        metodo: editandoId ? "PATCH" : "POST", cuerpo: { mesa_id: mesa ? +mesa : null, items: carrito },
      });
      cancelarEdicion(); await cargar();
    } catch (e) { setError(e.message); }
  };
  const eliminar = async (id) => {
    try {
      await api(`/pedidos/${id}`, { metodo: "DELETE" });
      setConfirmarEliminarId(null); setError(""); await cargar();
    } catch (e) { setError(e.message); }
  };
  const cobrar = async (id) => {
    setCobrando(true);
    setErrorCobro("");
    try {
      await api(`/pedidos/${id}/cobrar`, { metodo: "POST", cuerpo: { propina: Number(propina) || 0, metodo_pago: metodoPago } });
      await cargar();
      setCobroId(null);
    } catch (e) { setErrorCobro(e.message); }
    finally { setCobrando(false); }
  };
  return (
    <>
      {puedeCrear && <section>
        <h2>{editandoId ? `Editar pedido #${editandoId}` : "Nuevo pedido"}</h2>
        <select value={mesa} onChange={(e) => setMesa(e.target.value)}>
          <option value="">Para llevar</option>
          {mesas.map((m) => <option key={m.id} value={m.id}>{m.nombre}</option>)}
        </select>
        <div className="botones">
          {menu.map((pl) => <button key={pl.id} onClick={() => agregar(pl)}>{pl.nombre}<small>{dinero(pl.precio)}</small></button>)}
        </div>
        {menu.length === 0 && <p className="vacio">Primero crea platillos en Menú.</p>}
        {carrito.map((x, i) => (
          <div className="linea" key={`${x.platillo_id}-${i}`}>
            <b>{x.cantidad}×</b><span className="linea-nombre">{x.nombre}</span>
            <button type="button" className="boton-eliminar" aria-label={`Quitar ${x.nombre}`} title={`Quitar ${x.nombre}`} onClick={() => quitar(i)}><Trash2 size={18} /></button>
            <input placeholder="Nota (sin cebolla…)" value={x.nota} onChange={(e) => nota(i, e.target.value)} />
          </div>
        ))}
        {carrito.length > 0 && <button className="primario" onClick={enviar}>{editandoId ? "Guardar cambios" : "Enviar a cocina"}</button>}
        {editandoId && <button type="button" onClick={cancelarEdicion}>Cancelar edición</button>}
      </section>}
      <section>
        <h2>Cuentas abiertas</h2>
        {error && <p className="error">{error}</p>}
        {abiertos.length === 0 && <p className="vacio">No hay cuentas abiertas.</p>}
        {abiertos.map((a) => (
          <div className="tarjeta" key={a.id}>
            <div className="fila"><b>{a.mesa}</b><b>{dinero(a.total)}</b></div>
            {a.items.map((i, k) => <small key={k} className="bloque">{i.cantidad}× {i.nombre} {i.nota && `(${i.nota})`} — {i.estado}</small>)}
            {puedeCrear && a.editable && <div className="pedido-acciones">
              <button type="button" disabled={editandoId === a.id} onClick={() => iniciarEdicion(a)}>Editar</button>
              {confirmarEliminarId === a.id ? <>
                <span>¿Eliminar este pedido?</span>
                <button type="button" className="destructivo" onClick={() => eliminar(a.id)}>Confirmar</button>
                <button type="button" onClick={() => setConfirmarEliminarId(null)}>Cancelar</button>
              </> : <button type="button" className="destructivo" onClick={() => setConfirmarEliminarId(a.id)}><Trash2 size={16} aria-hidden="true" /><span>Eliminar</span></button>}
            </div>}
            {puedeCobrar && cobroId === a.id ? (
              <form className="pago" onSubmit={(e) => { e.preventDefault(); cobrar(a.id); }}>
                <label>Propina (MXN)
                  <input type="number" min="0" step="0.01" required value={propina} onChange={(e) => setPropina(e.target.value)} />
                </label>
                <label>Método de pago
                  <select value={metodoPago} onChange={(e) => setMetodoPago(e.target.value)}>
                    <option value="efectivo">Efectivo</option>
                    <option value="tarjeta">Tarjeta</option>
                    <option value="transferencia">Transferencia</option>
                  </select>
                </label>
                {errorCobro && <p className="error">{errorCobro}</p>}
                <div className="pago-acciones">
                  <button className="primario" type="submit" disabled={cobrando}>{cobrando ? "Procesando…" : "Confirmar cobro"}</button>
                  <button type="button" disabled={cobrando} onClick={() => { setCobroId(null); setErrorCobro(""); }}>Cancelar</button>
                </div>
              </form>
            ) : puedeCobrar ? (
              <button className="primario" onClick={() => { setCobroId(a.id); setPropina("0"); setMetodoPago("efectivo"); setErrorCobro(""); }}>Cobrar</button>
            ) : null}
          </div>
        ))}
      </section>
    </>
  );
}

/* ---------- cocina ---------- */
function Cocina() {
  const soloLectura = sesion()?.usuario.rol === "cocinero";
  const [items, setItems] = useState([]);
  const cargar = () => api("/cocina").then(setItems);
  useEffect(() => {
    cargar();
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/api/ws/cocina?token=${sesion().token}`);
    ws.onmessage = cargar;
    return () => ws.close();
  }, []);
  const mover = async (it) => {
    await api(`/cocina/items/${it.id}`, { metodo: "PATCH", cuerpo: { estado: it.estado === "pendiente" ? "preparando" : "listo" } });
    cargar();
  };
  return (
    <section>
      <h2>Pendientes en cocina</h2>
      {items.length === 0 && <p className="vacio">No hay pedidos pendientes.</p>}
      <div className="cocina">
        {items.map((it) => (
          <div className={"tarjeta " + it.estado} key={it.id}>
            <b>{it.cantidad}× {it.platillo}</b>
            <small>{it.mesa} · pedido #{it.pedido_id}</small>
            {it.nota && <em>{it.nota}</em>}
            {!soloLectura && <button className="primario" onClick={() => mover(it)}>{it.estado === "pendiente" ? "Empezar" : "Marcar listo"}</button>}
          </div>
        ))}
      </div>
    </section>
  );
}

/* ---------- menú y recetas ---------- */
function Menu() {
  const [lista, setLista] = useState([]);
  const [insumos, setInsumos] = useState([]);
  const [f, setF] = useState({ tipo: "comida", receta: [] });
  const [error, setError] = useState("");
  const cargar = () => api("/platillos").then(setLista);
  useEffect(() => { cargar(); api("/insumos").then(setInsumos); }, []);
  const addIng = () => setF({ ...f, receta: [...f.receta, { insumo_id: insumos[0]?.id, cantidad: 1 }] });
  const setIng = (i, k, v) => setF({ ...f, receta: f.receta.map((x, j) => (j === i ? { ...x, [k]: +v } : x)) });
  const guardar = async () => {
    try {
      await api("/platillos", { metodo: "POST", cuerpo: { ...f, precio: +f.precio } });
      setF({ tipo: "comida", receta: [] }); setError(""); cargar();
    } catch (e) { setError(e.message); }
  };
  return (
    <>
      <section>
        <h2>Nuevo platillo o bebida</h2>
        <input placeholder="Nombre" value={f.nombre || ""} onChange={(e) => setF({ ...f, nombre: e.target.value })} />
        <div className="barra-op">
          <select value={f.tipo} onChange={(e) => setF({ ...f, tipo: e.target.value })}><option value="comida">Comida</option><option value="bebida">Bebida</option></select>
          <input placeholder="Categoría" value={f.categoria || ""} onChange={(e) => setF({ ...f, categoria: e.target.value })} />
          <input placeholder="Precio" type="number" value={f.precio || ""} onChange={(e) => setF({ ...f, precio: e.target.value })} />
        </div>
        <h3>Receta</h3>
        {f.receta.map((x, i) => (
          <div className="barra-op" key={i}>
            <select value={x.insumo_id} onChange={(e) => setIng(i, "insumo_id", e.target.value)}>
              {insumos.map((n) => <option key={n.id} value={n.id}>{n.nombre} ({n.unidad})</option>)}
            </select>
            <input type="number" step="0.001" value={x.cantidad} onChange={(e) => setIng(i, "cantidad", e.target.value)} />
          </div>
        ))}
        <button onClick={addIng} disabled={!insumos.length}>+ Ingrediente</button>
        {!insumos.length && <p className="vacio">Agrega insumos en Almacén para armar recetas.</p>}
        {error && <p className="error">{error}</p>}
        <button className="primario" onClick={guardar}>Guardar</button>
      </section>
      <section>
        <h2>Menú actual</h2>
        {lista.map((p) => (
          <div className="tarjeta" key={p.id}>
            <div className="fila"><b>{p.nombre}</b><b>{dinero(p.precio)}</b></div>
            <small>{p.tipo} · costo {dinero(p.costo)} · margen {p.margen_pct}%</small>
          </div>
        ))}
      </section>
    </>
  );
}

/* ---------- almacén ---------- */
function Almacen() {
  const [lista, setLista] = useState([]);
  const [f, setF] = useState({});
  const [error, setError] = useState("");
  const cargar = () => api("/insumos").then(setLista);
  useEffect(() => { cargar(); }, []);
  const campo = (k, ph, tipo = "text") => (
    <input placeholder={ph} type={tipo} step="any" value={f[k] || ""} onChange={(e) => setF({ ...f, [k]: e.target.value })} />
  );
  const guardar = async () => {
    try {
      await api("/insumos", { metodo: "POST", cuerpo: { nombre: f.nombre, unidad: f.unidad, costo_unitario: +f.costo, cantidad: +f.cantidad || 0, minimo: +f.minimo || 0 } });
      setF({}); setError(""); cargar();
    } catch (e) { setError(e.message); }
  };
  const entrada = async (i) => {
    const cantidad = prompt(`Cantidad que entra de ${i.nombre} (${i.unidad})`);
    if (!cantidad) return;
    const costo = prompt("Nuevo costo unitario (deja vacío para no cambiarlo)", "");
    await api(`/insumos/${i.id}/entrada`, { metodo: "POST", cuerpo: { cantidad: +cantidad, costo_unitario: costo ? +costo : null } });
    cargar();
  };
  return (
    <>
      <section>
        <h2>Nuevo insumo</h2>
        {campo("nombre", "Nombre (ej. Tortilla)")}
        <div className="barra-op">{campo("unidad", "Unidad (kg, pza, l)")}{campo("costo", "Costo por unidad", "number")}</div>
        <div className="barra-op">{campo("cantidad", "Stock inicial", "number")}{campo("minimo", "Stock mínimo", "number")}</div>
        {error && <p className="error">{error}</p>}
        <button className="primario" onClick={guardar}>Guardar insumo</button>
      </section>
      <section>
        <h2>Existencias</h2>
        {lista.map((i) => (
          <div className={"tarjeta" + (i.bajo ? " alerta" : "")} key={i.id}>
            <div className="fila"><b>{i.nombre}</b><b>{Number(i.cantidad)} {i.unidad}</b></div>
            <small>{dinero(i.costo_unitario)} por {i.unidad} · mínimo {Number(i.minimo)} {i.bajo && "· stock bajo"}</small>
            <button onClick={() => entrada(i)}>Registrar entrada</button>
          </div>
        ))}
      </section>
    </>
  );
}

/* ---------- mesas ---------- */
function Mesas() {
  const [lista, setLista] = useState([]);
  const [f, setF] = useState({});
  const cargar = () => api("/mesas").then(setLista);
  useEffect(() => { cargar(); }, []);
  const guardar = async () => {
    await api("/mesas", { metodo: "POST", cuerpo: { nombre: f.nombre, capacidad: +f.capacidad || 4 } });
    setF({}); cargar();
  };
  return (
    <section>
      <h2>Mesas</h2>
      <div className="barra-op">
        <input placeholder="Nombre (Mesa 1, Terraza 2…)" value={f.nombre || ""} onChange={(e) => setF({ ...f, nombre: e.target.value })} />
        <input placeholder="Lugares" type="number" value={f.capacidad || ""} onChange={(e) => setF({ ...f, capacidad: e.target.value })} />
      </div>
      <button className="primario" onClick={guardar}>Agregar mesa</button>
      {lista.map((m) => <div className="tarjeta" key={m.id}><div className="fila"><b>{m.nombre}</b><span>{m.capacidad} lugares</span></div></div>)}
    </section>
  );
}

/* ---------- estructura ---------- */
const SECCIONES = {
  dashboard: ["Resumen", ["dueno", "gerente"], Dashboard],
  pedidos: ["Pedidos", ["dueno", "gerente", "mesero", "cajero"], Pedidos],
  cocina: ["Cocina", ["dueno", "gerente", "cocinero"], Cocina],
  menu: ["Menú", ["dueno", "gerente"], Menu],
  almacen: ["Almacén", ["dueno", "gerente"], Almacen],
  mesas: ["Mesas", ["dueno", "gerente"], Mesas],
  usuarios: ["Usuarios", ["dueno", "gerente"], Usuarios],
};

export default function App() {
  const [s, setS] = useState(sesion());
  const [tab, setTab] = useState(null);
  useEffect(() => {
    if (!s || s.usuario.codigo_restaurante) return;
    api("/auth/me").then(({ usuario }) => {
      const actualizada = { ...s, usuario: { ...s.usuario, ...usuario } };
      guardarSesion(actualizada);
      setS(actualizada);
    }).catch(() => {});
  }, [s]);
  if (!s) return <Acceso alEntrar={(x) => { guardarSesion(x); setS(x); }} />;
  const visibles = Object.entries(SECCIONES).filter(([, v]) => v[1].includes(s.usuario.rol));
  const actual = tab && SECCIONES[tab][1].includes(s.usuario.rol) ? tab : visibles[0][0];
  const Vista = SECCIONES[actual][2];
  const nombresRol = { dueno: "Dueño", gerente: "Gerente", mesero: "Mesero", cocinero: "Cocinero", cajero: "Cajero" };
  return (
    <div className="app">
      <header>
        <div className="cabecera-identidad">
          <b>{s.usuario.organizacion}</b>
          <small>{s.usuario.nombre} · {nombresRol[s.usuario.rol] || s.usuario.rol}{s.usuario.codigo_restaurante && ` · Código: ${s.usuario.codigo_restaurante}`}</small>
        </div>
        <button className="texto" onClick={salir}>Salir</button>
      </header>
      <main><Vista key={actual} /></main>
      <nav>{visibles.map(([k, v]) => <button key={k} className={k === actual ? "activo" : ""} onClick={() => setTab(k)}>{v[0]}</button>)}</nav>
    </div>
  );
}
