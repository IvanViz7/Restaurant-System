from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

Dinero = Numeric(12, 2)
Costo = Numeric(12, 4)
Cantidad = Numeric(12, 3)


def fk(tabla):
    return mapped_column(ForeignKey(f"{tabla}.id"), index=True)


class Organizacion(Base):
    __tablename__ = "organizaciones"
    __table_args__ = (Index("uq_organizaciones_codigo", "codigo", unique=True),)
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    codigo: Mapped[str] = mapped_column(String(40), nullable=False)


class Sucursal(Base):
    __tablename__ = "sucursales"
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    nombre: Mapped[str] = mapped_column(String(120))
    zona_horaria: Mapped[str] = mapped_column(String(60), default="America/Mexico_City")


class Usuario(Base):  # sin RLS: el login ocurre antes de conocer la organización
    __tablename__ = "usuarios"
    __table_args__ = (Index(
        "uq_usuarios_organizacion_usuario", "organizacion_id", text("lower(usuario)"),
        unique=True, postgresql_where=text("usuario IS NOT NULL"),
    ),)
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    sucursal_id: Mapped[int | None] = mapped_column(ForeignKey("sucursales.id"), nullable=True)
    nombre: Mapped[str] = mapped_column(String(120))
    usuario: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True)
    clave_hash: Mapped[str] = mapped_column(String(100))
    rol: Mapped[str] = mapped_column(String(20))  # dueno, gerente, mesero, cocinero, cajero


class Insumo(Base):  # catálogo compartido por toda la organización
    __tablename__ = "insumos"
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    nombre: Mapped[str] = mapped_column(String(120))
    unidad: Mapped[str] = mapped_column(String(20))
    costo_unitario: Mapped[Decimal] = mapped_column(Costo, default=0)


class Existencia(Base):  # stock por sucursal
    __tablename__ = "existencias"
    __table_args__ = (UniqueConstraint("sucursal_id", "insumo_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    sucursal_id: Mapped[int] = fk("sucursales")
    insumo_id: Mapped[int] = fk("insumos")
    cantidad: Mapped[Decimal] = mapped_column(Cantidad, default=0)
    minimo: Mapped[Decimal] = mapped_column(Cantidad, default=0)


class Platillo(Base):  # comidas y bebidas
    __tablename__ = "platillos"
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    nombre: Mapped[str] = mapped_column(String(120))
    tipo: Mapped[str] = mapped_column(String(10), default="comida")  # comida | bebida
    categoria: Mapped[str] = mapped_column(String(60), default="")
    precio: Mapped[Decimal] = mapped_column(Dinero)
    activo: Mapped[bool] = mapped_column(default=True)


class RecetaItem(Base):
    __tablename__ = "receta_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    platillo_id: Mapped[int] = fk("platillos")
    insumo_id: Mapped[int] = fk("insumos")
    cantidad: Mapped[Decimal] = mapped_column(Cantidad)


class Mesa(Base):
    __tablename__ = "mesas"
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    sucursal_id: Mapped[int] = fk("sucursales")
    nombre: Mapped[str] = mapped_column(String(60))
    capacidad: Mapped[int] = mapped_column(default=4)


class Pedido(Base):
    __tablename__ = "pedidos"
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    sucursal_id: Mapped[int] = fk("sucursales")
    mesa_id: Mapped[int | None] = mapped_column(ForeignKey("mesas.id"), nullable=True)
    mesero_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    estado: Mapped[str] = mapped_column(String(10), default="abierto")  # abierto | cobrado
    propina: Mapped[Decimal] = mapped_column(Dinero, default=0)
    metodo_pago: Mapped[str | None] = mapped_column(String(20), nullable=True)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cobrado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)


class PedidoItem(Base):
    __tablename__ = "pedido_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    pedido_id: Mapped[int] = fk("pedidos")
    platillo_id: Mapped[int] = fk("platillos")
    cantidad: Mapped[int] = mapped_column(default=1)
    consumo_registrado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    precio_unitario: Mapped[Decimal] = mapped_column(Dinero)  # precio al momento de vender
    costo_unitario: Mapped[Decimal] = mapped_column(Costo)    # costo al momento de vender
    nota: Mapped[str] = mapped_column(String(200), default="")
    estado_cocina: Mapped[str] = mapped_column(String(12), default="pendiente")  # pendiente | preparando | listo


class PedidoItemInsumo(Base):
    __tablename__ = "pedido_item_insumos"
    __table_args__ = (UniqueConstraint("pedido_item_id", "insumo_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = fk("organizaciones")
    pedido_item_id: Mapped[int] = fk("pedido_items")
    insumo_id: Mapped[int] = fk("insumos")
    cantidad: Mapped[Decimal] = mapped_column(Cantidad)
