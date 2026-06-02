# h_validadores.py

from copy import deepcopy
from datetime import datetime

from a_00_config import *
from a_db import db

# =========================================================
# UTILIDAD
# =========================================================

def norm(x):
    return x.strip().lower() if isinstance(x, str) else x


def to_float(x):
    try:

        if x in (None, ""):
            return None

        return float(x)

    except:
        return None


def parse_fecha(fecha):

    try:

        return datetime.strptime(
            fecha,
            "%Y-%m-%d %H:%M:%S"
        )

    except:

        return datetime.min


# =========================================================
# VALIDACIONES BÁSICAS
# =========================================================

def validar_stock_none(i, evento):

    stock = to_float(
        evento.get("stock_reconstruido")
    )

    if stock is None:

        return {
            "indice": i,
            "tipo": "stock_none",
            "detalle": evento
        }

    return None


def validar_valores_none(i, evento):

    va = to_float(
        evento.get("valor_anterior_reconstruido")
    )

    nv = to_float(
        evento.get("nuevo_valor_reconstruido")
    )

    if va is None or nv is None:

        return {
            "indice": i,
            "tipo": "valor_none",
            "detalle": evento
        }

    return None


# =========================================================
# VALIDAR CONSISTENCIA
# =========================================================

def validar_consistencia_con_stock_previo(
    i,
    evento,
    evento_previo
):

    if not evento_previo:
        return None

    mov = norm(
        evento.get("movimiento")
    )

    # IGNORAR
    if mov in MOVIMIENTOS_IGNORE:
        return None

    # RESETEOS DIRECTOS
    if (
        mov in MOVIMIENTOS_RESETEO
        or mov in MOVIMIENTOS_CONTEO_DIRECTO
    ):
        return None

    stock_previo = to_float(
        evento_previo.get("stock_reconstruido")
    )

    valor_anterior = to_float(
        evento.get("valor_anterior")
    )

    if (
        stock_previo is None
        or valor_anterior is None
    ):
        return None

    if abs(
        stock_previo - valor_anterior
    ) > TOLERANCIA_NUMERICA:

        return {
            "indice": i,
            "tipo": "inconsistencia_valor_anterior",
            "stock_previo": stock_previo,
            "valor_anterior": valor_anterior,
            "detalle": evento
        }

    return None


# =========================================================
# VALIDAR NUEVO VALOR
# =========================================================

def validar_nuevo_valor(
    i,
    evento
):

    nv_original = to_float(
        evento.get("nuevo_valor")
    )

    nv_reconstruido = to_float(
        evento.get("nuevo_valor_reconstruido")
    )

    mov = norm(
        evento.get("movimiento")
    )

    if mov in MOVIMIENTOS_IGNORE:
        return None

    if (
        nv_original is None
        or nv_reconstruido is None
    ):
        return None

    if abs(
        nv_original - nv_reconstruido
    ) > TOLERANCIA_NUMERICA:

        return {
            "indice": i,
            "tipo": "inconsistencia_nuevo_valor",
            "nuevo_valor_original": nv_original,
            "nuevo_valor_reconstruido": nv_reconstruido,
            "detalle": evento
        }

    return None


# =========================================================
# VALIDAR SALTOS
# =========================================================

def validar_salto_excesivo(
    i,
    evento,
    evento_previo
):

    if not evento_previo:
        return None

    actual = to_float(
        evento.get("stock_reconstruido")
    )

    previo = to_float(
        evento_previo.get("stock_reconstruido")
    )

    if actual is None or previo is None:
        return None

    if abs(actual - previo) > SALTO_MAXIMO_PERMITIDO:

        return {
            "indice": i,
            "tipo": "salto_excesivo_stock",
            "stock_previo": previo,
            "stock_actual": actual,
            "detalle": evento
        }

    return None


# =========================================================
# VALIDAR NEGATIVOS
# =========================================================

def validar_stock_negativo(
    i,
    evento
):

    stock = to_float(
        evento.get("stock_reconstruido")
    )

    if stock is None:
        return None

    if stock < UMBRAL_NEGATIVO:

        return {
            "indice": i,
            "tipo": "stock_negativo",
            "stock": stock,
            "detalle": evento
        }

    return None


# =========================================================
# VALIDAR MOVIMIENTOS SIN CANTIDAD
# =========================================================

def validar_movimiento_sin_cantidad(
    i,
    evento
):

    mov = norm(
        evento.get("movimiento")
    )

    if mov not in (
        "ventas detalladas",
        "facturas detalladas"
    ):
        return None

    cantidad = to_float(
        evento.get("cantidad")
    )

    if cantidad is None:

        return {
            "indice": i,
            "tipo": "movimiento_sin_cantidad",
            "detalle": evento
        }

    return None


# =========================================================
# MOTOR PRINCIPAL
# =========================================================

def validar_historial(historial):

    historial = deepcopy(historial)

    inconsistencias = []

    for i, evento in enumerate(historial):

        previo = (
            historial[i - 1]
            if i > 0
            else None
        )

        validaciones = [

            validar_stock_none(
                i,
                evento
            ),

            validar_valores_none(
                i,
                evento
            ),

            validar_consistencia_con_stock_previo(
                i,
                evento,
                previo
            ),

            validar_nuevo_valor(
                i,
                evento
            ),

            validar_salto_excesivo(
                i,
                evento,
                previo
            ),

            validar_stock_negativo(
                i,
                evento
            ),

            validar_movimiento_sin_cantidad(
                i,
                evento
            )
        ]

        for v in validaciones:

            if v:
                inconsistencias.append(v)

    return inconsistencias


# =========================================================
# RESUMEN
# =========================================================

def resumir_inconsistencias(
    inconsistencias
):

    resumen = {}

    for e in inconsistencias:

        tipo = e["tipo"]

        resumen[tipo] = (
            resumen.get(tipo, 0) + 1
        )

    return resumen


# =========================================================
# API SIMPLE
# =========================================================

def ejecutar_validaciones(
    historial
):

    inconsistencias = validar_historial(
        historial
    )

    return {
        "total_inconsistencias": len(
            inconsistencias
        ),
        "inconsistencias": inconsistencias,
        "resumen": resumir_inconsistencias(
            inconsistencias
        )
    }