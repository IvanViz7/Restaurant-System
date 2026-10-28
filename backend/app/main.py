from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import anyio
import re
import secrets
from fastapi import APIRouter, Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy import and_, func, select, text

from .db import Base, Sesion, engine
from .migraciones import aplicar_migraciones
from .modelos import (Existencia, Insumo, Mesa, Organizacion, Pedido, PedidoItem, PedidoItemInsumo, Platillo,
                      RecetaItem, Sucursal, Usuario)
from .seguridad import crear_token, hashear, leer_token, verificar

TABLAS_RLS = ["sucursales", "insumos", "existencias", "platillos", "receta_items",
              "mesas", "pedidos", "pedido_items", "pedido_item_insumos"]
ROLES = {"dueno", "gerente", "mesero", "cocinero", "cajero"}


def preparar():
    """Crea tablas y activa Row Level Security: cada fila solo es visible para su organización."""
    Base.metadata.create_all(engine)
    aplicar_migraciones()
    cond = "organizacion_id = NULLIF(current_setting('app.org_id', true), '')::int"
    with engine.begin() as c:
        for t in TABLAS_RLS:
            c.execute(text(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY"))
            c.execute(text(f"ALTER TABLE {t} FORCE ROW LEVEL SECURITY"))
            c.execute(text(f"DROP POLICY IF EXISTS aislamiento ON {t}"))
            c.execute(text(f"CREATE POLICY aislamiento ON {t} USING ({cond}) WITH CHECK ({cond})"))


@asynccontextmanager
async def vida(_):
    preparar()
    yield


app = FastAPI(title="Sistema Restaurante", lifespan=vida,
              docs_url="/api/docs", openapi_url="/api/openapi.json")
r = APIRouter(prefix="/api")


# ---------- dependencias ----------
def ctx(c=Depends(HTTPBearer())):
    try:
        return leer_token(c.credentials)
    except Exception:
        raise HTTPException(401, "Sesión inválida o vencida")


def solo(*roles):
    def f(p=Depends(ctx)):
        if p["rol"] not in roles:
            raise HTTPException(403, "No tienes permiso para esto")
        return p
    return f


def db(p=Depends(ctx)):
    s = Sesion()
    try:
        s.execute(text("SELECT set_config('app.org_id', :o, true)"), {"o": str(p["org"])})
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def D(x) -> Decimal:
    return Decimal(str(x))


def sucursal_activa(p, s, sid=None) -> int:
    if p["rol"] in {"mesero", "cocinero", "cajero"}:
        sid = p["suc"]
        if sid is None:
            raise HTTPException(403, "Tu usuario no tiene una sucursal asignada")
    else:
        sid = p["suc"] or sid or s.scalar(select(Sucursal.id).order_by(Sucursal.id))
    if not s.get(Sucursal, sid):  # RLS: solo ve sucursales de su organización
        raise HTTPException(404, "Sucursal no encontrada")
    return sid


def costo_platillo(s, pid) -> Decimal:
    return s.scalar(select(func.coalesce(func.sum(RecetaItem.cantidad * Insumo.costo_unitario), 0))
                    .select_from(RecetaItem).join(Insumo, Insumo.id == RecetaItem.insumo_id)
                    .where(RecetaItem.platillo_id == pid))


def existencia(s, org, sid, iid) -> Existencia:
    e = s.scalar(select(Existencia).where(Existencia.sucursal_id == sid, Existencia.insumo_id == iid))
    if not e:
        e = Existencia(organizacion_id=org, sucursal_id=sid, insumo_id=iid, cantidad=D(0), minimo=D(0))
        s.add(e)
        s.flush()
    return e


def registrar_consumo(s, item, org, sid):
    consumos = {}
    for ri in s.scalars(select(RecetaItem).where(RecetaItem.platillo_id == item.platillo_id)):
        consumos[ri.insumo_id] = consumos.get(ri.insumo_id, D(0)) + D(ri.cantidad) * item.cantidad
    item.consumo_registrado = True
    s.flush()
    for iid, cantidad in consumos.items():
        existencia(s, org, sid, iid).cantidad -= cantidad
        s.add(PedidoItemInsumo(organizacion_id=org, pedido_item_id=item.id, insumo_id=iid, cantidad=cantidad))


def restaurar_consumo_pedido(s, ped):
    items = list(s.scalars(select(PedidoItem).where(PedidoItem.pedido_id == ped.id)))
    if any(not item.consumo_registrado for item in items):
        raise HTTPException(409, "Este pedido es anterior al registro de inventario y no se puede modificar")
    for item in items:
        consumos = list(s.scalars(select(PedidoItemInsumo).where(PedidoItemInsumo.pedido_item_id == item.id)))
        for consumo in consumos:
            existencia(s, ped.organizacion_id, ped.sucursal_id, consumo.insumo_id).cantidad += consumo.cantidad
            s.delete(consumo)
        s.flush()
        s.delete(item)


# ---------- tiempo real (cocina) ----------
conexiones: dict[int, set[WebSocket]] = {}


async def difundir(org: int):
    for ws in list(conexiones.get(org, ())):
        try:
            await ws.send_text("actualizar")
        except Exception:
            conexiones[org].discard(ws)


@r.websocket("/ws/cocina")
async def ws_cocina(ws: WebSocket, token: str):
    try:
        p = leer_token(token)
    except Exception:
        await ws.close(4401)
        return
    if p.get("rol") not in {"dueno", "gerente", "cocinero"}:
        await ws.close(4403)
        return
    await ws.accept()
    conexiones.setdefault(p["org"], set()).add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        conexiones[p["org"]].discard(ws)


# ---------- esquemas ----------
class RegistroIn(BaseModel):
    organizacion: str
    sucursal: str = "Principal"
    nombre: str
    email: str
    clave: str


class LoginIn(BaseModel):
    codigo_restaurante: str
    usuario: str | None = None
    email: str | None = None
    clave: str


class UsuarioIn(BaseModel):
    nombre: str
    usuario: str
    clave: str
    rol: str
    sucursal_id: int | None = None


class InsumoIn(BaseModel):
    nombre: str
    unidad: str
    costo_unitario: float
    cantidad: float = 0
    minimo: float = 0


class EntradaIn(BaseModel):
    cantidad: float
    costo_unitario: float | None = None


class RecetaIn(BaseModel):
    insumo_id: int
    cantidad: float


class PlatilloIn(BaseModel):
    nombre: str
    tipo: str = "comida"
    categoria: str = ""
    precio: float
    receta: list[RecetaIn] = []


class MesaIn(BaseModel):
    nombre: str
    capacidad: int = 4


class ItemIn(BaseModel):
    platillo_id: int
    cantidad: int = 1
    nota: str = ""


class PedidoIn(BaseModel):
    mesa_id: int | None = None
    items: list[ItemIn]


class PedidoActualizarIn(PedidoIn):
    pass


class CobroIn(BaseModel):
    propina: float = 0
    metodo_pago: str = "efectivo"


class EstadoIn(BaseModel):
    estado: str


# ---------- auth ----------
def sesion_out(u, org):
    return {"token": crear_token(u),
            "usuario": {"nombre": u.nombre, "rol": u.rol, "organizacion": org.nombre,
                        "codigo_restaurante": org.codigo, "usuario": u.usuario,
                        "sucursal_id": u.sucursal_id}}


@r.post("/auth/registro")
def registro(d: RegistroIn):
    with Sesion() as s:
        email = d.email.strip().lower()
        if s.scalar(select(Usuario).where(func.lower(Usuario.email) == email)):
            raise HTTPException(409, "Ese correo ya está registrado")
        o = Organizacion(nombre=d.organizacion.strip(), codigo=f"rest-{secrets.token_hex(8)}")
        s.add(o)
        s.flush()
        s.execute(text("SELECT set_config('app.org_id', :o, true)"), {"o": str(o.id)})
        s.add(Sucursal(organizacion_id=o.id, nombre=d.sucursal))
        u = Usuario(organizacion_id=o.id, nombre=d.nombre.strip(), usuario="dueno", email=email,
                    clave_hash=hashear(d.clave), rol="dueno")
        s.add(u)
        s.commit()
        return sesion_out(u, o)


@r.post("/auth/login")
def login(d: LoginIn):
    with Sesion() as s:
        codigo = d.codigo_restaurante.strip().lower()
        identificador = (d.usuario or d.email or "").strip().lower()
        if "@" in identificador:
            identidad = func.lower(Usuario.email) == identificador
        else:
            identidad = func.lower(Usuario.usuario) == identificador
        u = s.scalar(select(Usuario).join(Organizacion).where(Organizacion.codigo == codigo, identidad))
        if not u or not verificar(d.clave, u.clave_hash):
            raise HTTPException(401, "Restaurante, usuario/correo o contraseña incorrectos")
        org = s.get(Organizacion, u.organizacion_id)
        return sesion_out(u, org)


@r.get("/auth/me")
def usuario_actual(p=Depends(ctx), s=Depends(db)):
    u = s.get(Usuario, int(p["sub"]))
    org = s.get(Organizacion, p["org"])
    if not u or not org or u.organizacion_id != p["org"]:
        raise HTTPException(401, "Sesión inválida o vencida")
    return {"usuario": {"nombre": u.nombre, "rol": u.rol, "usuario": u.usuario,
                        "organizacion": org.nombre,
                        "codigo_restaurante": org.codigo, "sucursal_id": u.sucursal_id}}


@r.post("/usuarios")
def crear_usuario(d: UsuarioIn, p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    if d.rol not in {"gerente", "mesero", "cocinero", "cajero"}:
        raise HTTPException(400, "Rol no válido")
    if d.rol in {"mesero", "cocinero", "cajero"} and d.sucursal_id is None:
        raise HTTPException(400, "Este rol requiere una sucursal asignada")
    if d.sucursal_id and not s.get(Sucursal, d.sucursal_id):
        raise HTTPException(404, "Sucursal no encontrada")
    usuario = d.usuario.strip().lower()
    if not re.fullmatch(r"[a-z0-9._-]{3,32}", usuario):
        raise HTTPException(400, "El usuario debe tener entre 3 y 32 caracteres: letras, números, punto, guion o guion bajo")
    if s.scalar(select(Usuario).where(
        Usuario.organizacion_id == p["org"], func.lower(Usuario.usuario) == usuario
    )):
        raise HTTPException(409, "Ese usuario ya está registrado en este restaurante")
    u = Usuario(organizacion_id=p["org"], sucursal_id=d.sucursal_id, nombre=d.nombre.strip(),
                usuario=usuario, email=None, clave_hash=hashear(d.clave), rol=d.rol)
    s.add(u)
    s.flush()
    return {"id": u.id}


@r.get("/usuarios")
def listar_usuarios(p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    us = s.scalars(select(Usuario).where(Usuario.organizacion_id == p["org"]))
    return [{"id": u.id, "nombre": u.nombre, "usuario": u.usuario, "email": u.email,
             "rol": u.rol, "sucursal_id": u.sucursal_id} for u in us]


@r.get("/sucursales")
def listar_sucursales(p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    return [{"id": suc.id, "nombre": suc.nombre}
            for suc in s.scalars(select(Sucursal).where(Sucursal.organizacion_id == p["org"]).order_by(Sucursal.id))]


# ---------- almacén ----------
@r.get("/insumos")
def insumos(sucursal_id: int | None = None,
            p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    sid = sucursal_activa(p, s, sucursal_id)
    ex = {e.insumo_id: e for e in s.scalars(select(Existencia).where(Existencia.sucursal_id == sid))}
    out = []
    for i in s.scalars(select(Insumo).order_by(Insumo.nombre)):
        e = ex.get(i.id)
        cant, mini = (e.cantidad, e.minimo) if e else (D(0), D(0))
        out.append({"id": i.id, "nombre": i.nombre, "unidad": i.unidad, "costo_unitario": i.costo_unitario,
                    "cantidad": cant, "minimo": mini, "bajo": mini > 0 and cant <= mini})
    return out


@r.post("/insumos")
def crear_insumo(d: InsumoIn, sucursal_id: int | None = None,
                 p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    sid = sucursal_activa(p, s, sucursal_id)
    i = Insumo(organizacion_id=p["org"], nombre=d.nombre, unidad=d.unidad, costo_unitario=D(d.costo_unitario))
    s.add(i)
    s.flush()
    e = existencia(s, p["org"], sid, i.id)
    e.cantidad, e.minimo = D(d.cantidad), D(d.minimo)
    return {"id": i.id}


@r.post("/insumos/{iid}/entrada")
def entrada_insumo(iid: int, d: EntradaIn, sucursal_id: int | None = None,
                   p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    sid = sucursal_activa(p, s, sucursal_id)
    i = s.get(Insumo, iid)
    if not i:
        raise HTTPException(404, "Insumo no encontrado")
    e = existencia(s, p["org"], sid, iid)
    e.cantidad += D(d.cantidad)
    if d.costo_unitario is not None:
        i.costo_unitario = D(d.costo_unitario)
    return {"cantidad": e.cantidad}


# ---------- menú y recetas ----------
@r.get("/platillos")
def platillos(p=Depends(solo("dueno", "gerente", "mesero")), s=Depends(db)):
    out = []
    for pl in s.scalars(select(Platillo).where(Platillo.activo).order_by(Platillo.tipo, Platillo.nombre)):
        c = costo_platillo(s, pl.id)
        out.append({"id": pl.id, "nombre": pl.nombre, "tipo": pl.tipo, "categoria": pl.categoria,
                    "precio": pl.precio, "costo": c,
                    "margen_pct": round(float((pl.precio - c) / pl.precio * 100), 1) if pl.precio else 0})
    return out


@r.post("/platillos")
def crear_platillo(d: PlatilloIn, p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    pl = Platillo(organizacion_id=p["org"], nombre=d.nombre, tipo=d.tipo, categoria=d.categoria, precio=D(d.precio))
    s.add(pl)
    s.flush()
    for ri in d.receta:
        if not s.get(Insumo, ri.insumo_id):
            raise HTTPException(404, "Insumo no encontrado")
        s.add(RecetaItem(organizacion_id=p["org"], platillo_id=pl.id, insumo_id=ri.insumo_id, cantidad=D(ri.cantidad)))
    return {"id": pl.id}


# ---------- mesas ----------
@r.get("/mesas")
def mesas(sucursal_id: int | None = None,
           p=Depends(solo("dueno", "gerente", "mesero")), s=Depends(db)):
    sid = sucursal_activa(p, s, sucursal_id)
    return [{"id": m.id, "nombre": m.nombre, "capacidad": m.capacidad}
            for m in s.scalars(select(Mesa).where(Mesa.sucursal_id == sid).order_by(Mesa.id))]


@r.post("/mesas")
def crear_mesa(d: MesaIn, sucursal_id: int | None = None,
               p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    m = Mesa(organizacion_id=p["org"], sucursal_id=sucursal_activa(p, s, sucursal_id),
             nombre=d.nombre, capacidad=d.capacidad)
    s.add(m)
    s.flush()
    return {"id": m.id}


# ---------- pedidos ----------
@r.post("/pedidos")
def crear_pedido(d: PedidoIn, sucursal_id: int | None = None,
                 p=Depends(solo("dueno", "gerente", "mesero")), s=Depends(db)):
    if not d.items:
        raise HTTPException(400, "El pedido no tiene platillos")
    org, sid = p["org"], sucursal_activa(p, s, sucursal_id)
    if d.mesa_id:
        m = s.get(Mesa, d.mesa_id)
        if not m or m.sucursal_id != sid:
            raise HTTPException(404, "Mesa no encontrada")
    ped = Pedido(organizacion_id=org, sucursal_id=sid, mesa_id=d.mesa_id, mesero_id=int(p["sub"]))
    s.add(ped)
    s.flush()
    for it in d.items:
        if it.cantidad < 1:
            raise HTTPException(400, "La cantidad debe ser mayor a cero")
        pl = s.get(Platillo, it.platillo_id)
        if not pl or not pl.activo:
            raise HTTPException(404, "Platillo no disponible")
        item = PedidoItem(organizacion_id=org, pedido_id=ped.id, platillo_id=pl.id, cantidad=it.cantidad,
                          precio_unitario=pl.precio, costo_unitario=costo_platillo(s, pl.id), nota=it.nota)
        s.add(item)
        registrar_consumo(s, item, org, sid)
    pid = ped.id
    s.commit()
    anyio.from_thread.run(difundir, org)
    return {"id": pid}


@r.get("/pedidos")
def pedidos(estado: str = "abierto", sucursal_id: int | None = None,
            p=Depends(solo("dueno", "gerente", "mesero", "cajero")), s=Depends(db)):
    sid = sucursal_activa(p, s, sucursal_id)
    out = []
    q = select(Pedido).where(Pedido.sucursal_id == sid, Pedido.estado == estado).order_by(Pedido.id.desc()).limit(50)
    for pd in s.scalars(q):
        filas = s.execute(select(PedidoItem, Platillo.nombre).join(Platillo, Platillo.id == PedidoItem.platillo_id)
                          .where(PedidoItem.pedido_id == pd.id)).all()
        m = s.get(Mesa, pd.mesa_id) if pd.mesa_id else None
        out.append({"id": pd.id, "mesa": m.nombre if m else "Para llevar", "mesa_id": pd.mesa_id,
                "editable": all(i.estado_cocina == "pendiente" and i.consumo_registrado for i, _ in filas),
                    "total": sum(i.precio_unitario * i.cantidad for i, _ in filas),
                "items": [{"id": i.id, "platillo_id": i.platillo_id, "nombre": n,
                       "cantidad": i.cantidad, "nota": i.nota, "estado": i.estado_cocina}
                              for i, n in filas]})
    return out


@r.patch("/pedidos/{pid}")
def editar_pedido(pid: int, d: PedidoActualizarIn, sucursal_id: int | None = None,
                  p=Depends(solo("dueno", "gerente", "mesero")), s=Depends(db)):
    if not d.items:
        raise HTTPException(400, "El pedido debe conservar al menos un platillo")
    ped = s.get(Pedido, pid)
    sid = sucursal_activa(p, s, sucursal_id)
    if not ped or ped.sucursal_id != sid or ped.estado != "abierto":
        raise HTTPException(404, "Pedido no encontrado o ya cobrado")
    actuales = list(s.scalars(select(PedidoItem).where(PedidoItem.pedido_id == pid)))
    if any(item.estado_cocina != "pendiente" for item in actuales):
        raise HTTPException(409, "No se puede editar un pedido cuya preparación ya comenzó")
    restaurar_consumo_pedido(s, ped)
    if d.mesa_id:
        mesa = s.get(Mesa, d.mesa_id)
        if not mesa or mesa.sucursal_id != sid:
            raise HTTPException(404, "Mesa no encontrada")
    ped.mesa_id = d.mesa_id
    for entrada in d.items:
        if entrada.cantidad < 1:
            raise HTTPException(400, "La cantidad debe ser mayor a cero")
        platillo = s.get(Platillo, entrada.platillo_id)
        if not platillo or not platillo.activo:
            raise HTTPException(404, "Platillo no disponible")
        item = PedidoItem(organizacion_id=p["org"], pedido_id=ped.id, platillo_id=platillo.id,
                          cantidad=entrada.cantidad, precio_unitario=platillo.precio,
                          costo_unitario=costo_platillo(s, platillo.id), nota=entrada.nota)
        s.add(item)
        registrar_consumo(s, item, p["org"], sid)
    s.commit()
    anyio.from_thread.run(difundir, p["org"])
    return {"ok": True}


@r.delete("/pedidos/{pid}")
def eliminar_pedido(pid: int, sucursal_id: int | None = None,
                    p=Depends(solo("dueno", "gerente", "mesero")), s=Depends(db)):
    ped = s.get(Pedido, pid)
    sid = sucursal_activa(p, s, sucursal_id)
    if not ped or ped.sucursal_id != sid or ped.estado != "abierto":
        raise HTTPException(404, "Pedido no encontrado o ya cobrado")
    actuales = list(s.scalars(select(PedidoItem).where(PedidoItem.pedido_id == pid)))
    if any(item.estado_cocina != "pendiente" for item in actuales):
        raise HTTPException(409, "No se puede eliminar un pedido cuya preparación ya comenzó")
    restaurar_consumo_pedido(s, ped)
    s.flush()
    s.delete(ped)
    s.commit()
    anyio.from_thread.run(difundir, p["org"])
    return {"ok": True}


@r.post("/pedidos/{pid}/cobrar")
def cobrar(pid: int, d: CobroIn, sucursal_id: int | None = None,
           p=Depends(solo("dueno", "gerente", "cajero", "mesero")), s=Depends(db)):
    sid = sucursal_activa(p, s, sucursal_id)
    ped = s.get(Pedido, pid)
    if not ped or ped.sucursal_id != sid or ped.estado != "abierto":
        raise HTTPException(404, "Pedido no encontrado o ya cobrado")
    ped.estado, ped.propina, ped.metodo_pago = "cobrado", D(d.propina), d.metodo_pago
    ped.cobrado_en = datetime.now(timezone.utc)
    s.commit()
    anyio.from_thread.run(difundir, p["org"])
    return {"ok": True}


# ---------- cocina (KDS) ----------
@r.get("/cocina")
def cocina(sucursal_id: int | None = None,
           p=Depends(solo("dueno", "gerente", "cocinero")), s=Depends(db)):
    sid = sucursal_activa(p, s, sucursal_id)
    q = (select(PedidoItem, Platillo.nombre.label("platillo"), Mesa.nombre.label("mesa"))
         .join(Pedido, Pedido.id == PedidoItem.pedido_id)
         .join(Platillo, Platillo.id == PedidoItem.platillo_id)
         .outerjoin(Mesa, Mesa.id == Pedido.mesa_id)
         .where(Pedido.sucursal_id == sid, Pedido.estado == "abierto",
                PedidoItem.estado_cocina.in_(["pendiente", "preparando"]))
         .order_by(PedidoItem.id))
    return [{"id": i.id, "pedido_id": i.pedido_id, "platillo": n, "mesa": m or "Para llevar",
             "cantidad": i.cantidad, "nota": i.nota, "estado": i.estado_cocina} for i, n, m in s.execute(q)]


@r.patch("/cocina/items/{iid}")
def estado_item(iid: int, d: EstadoIn, p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    if d.estado not in ("pendiente", "preparando", "listo"):
        raise HTTPException(400, "Estado no válido")
    i = s.get(PedidoItem, iid)
    if not i:
        raise HTTPException(404, "Platillo no encontrado")
    i.estado_cocina = d.estado
    s.commit()
    anyio.from_thread.run(difundir, p["org"])
    return {"ok": True}


# ---------- métricas ----------
def totales(s, sid, desde, hasta):
    cobrado = and_(Pedido.estado == "cobrado", Pedido.sucursal_id == sid,
                   Pedido.cobrado_en >= desde, Pedido.cobrado_en < hasta)
    ventas, costo = s.execute(
        select(func.coalesce(func.sum(PedidoItem.cantidad * PedidoItem.precio_unitario), 0),
               func.coalesce(func.sum(PedidoItem.cantidad * PedidoItem.costo_unitario), 0))
        .select_from(PedidoItem).join(Pedido, Pedido.id == PedidoItem.pedido_id).where(cobrado)).one()
    n, propinas = s.execute(select(func.count(Pedido.id), func.coalesce(func.sum(Pedido.propina), 0)).where(cobrado)).one()
    return float(ventas), float(costo), n, float(propinas)


@r.get("/metricas/resumen")
def resumen(dias: int = 30, sucursal_id: int | None = None, p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    sid = sucursal_activa(p, s, sucursal_id)
    ahora = datetime.now(timezone.utc)
    ini = ahora - timedelta(days=dias)
    v, c, n, prop = totales(s, sid, ini, ahora)
    v0, *_ = totales(s, sid, ini - timedelta(days=dias), ini)
    return {"ventas": v, "costo": c, "utilidad": v - c, "food_cost_pct": round(c / v * 100, 1) if v else 0,
            "pedidos": n, "ticket_promedio": round(v / n, 2) if n else 0, "propinas": prop,
            "ventas_previas": v0, "variacion_pct": round((v - v0) / v0 * 100, 1) if v0 else None}


@r.get("/metricas/platillos")
def metricas_platillos(dias: int = 30, sucursal_id: int | None = None,
                       p=Depends(solo("dueno", "gerente")), s=Depends(db)):
    sid = sucursal_activa(p, s, sucursal_id)
    desde = datetime.now(timezone.utc) - timedelta(days=dias)
    cobrados = select(Pedido.id).where(Pedido.estado == "cobrado", Pedido.sucursal_id == sid, Pedido.cobrado_en >= desde)
    q = (select(Platillo.id, Platillo.nombre, Platillo.tipo,
                func.coalesce(func.sum(PedidoItem.cantidad), 0),
                func.coalesce(func.sum(PedidoItem.cantidad * PedidoItem.precio_unitario), 0),
                func.coalesce(func.sum(PedidoItem.cantidad * PedidoItem.costo_unitario), 0))
         .select_from(Platillo)
         .outerjoin(PedidoItem, and_(PedidoItem.platillo_id == Platillo.id, PedidoItem.pedido_id.in_(cobrados)))
         .where(Platillo.activo).group_by(Platillo.id))
    out = []
    for pid, nombre, tipo, u, ing, cos in s.execute(q):
        ing, cos = float(ing), float(cos)
        out.append({"id": pid, "nombre": nombre, "tipo": tipo, "unidades": int(u), "ingresos": ing,
                    "costo": cos, "utilidad": ing - cos, "margen_pct": round((ing - cos) / ing * 100, 1) if ing else 0})
    return out


@r.get("/salud")
def salud():
    return {"ok": True}


app.include_router(r)
