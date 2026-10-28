import os
import time

import bcrypt
import jwt

SECRETO = os.environ["JWT_SECRET"]


def hashear(clave: str) -> str:
    return bcrypt.hashpw(clave.encode(), bcrypt.gensalt()).decode()


def verificar(clave: str, hash_: str) -> bool:
    return bcrypt.checkpw(clave.encode(), hash_.encode())


def crear_token(u) -> str:
    datos = {"sub": str(u.id), "org": u.organizacion_id, "suc": u.sucursal_id,
             "rol": u.rol, "exp": int(time.time()) + 12 * 3600}
    return jwt.encode(datos, SECRETO, "HS256")


def leer_token(token: str) -> dict:
    return jwt.decode(token, SECRETO, ["HS256"])
