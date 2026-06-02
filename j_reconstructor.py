# j_reconstructor.py

from copy import deepcopy
from datetime import datetime
from a_00_config import *
from a_db import *
from b_loader_movimientos import obtener_eventos
from e_sugeridor_correcciones import buscar_ultimo_positivo


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


def round_safe(x):
    try:
        return round(float(x), 6)
    except:
        return x


def parse_fecha(fecha):
    try:
        return datetime.strptime(
            fecha,
            "%Y-%m-%d %H:%M:%S"
        )
    except:
        return datetime.min


# =========================================================
# DETERMINAR TIPO DE RECONSTRUCCIÓN
# =========================================================

def es_movimiento_reseteo(mov):

    mov = norm(mov)

    return (
        mov in MOVIMIENTOS_RESETEO
        or mov in MOVIMIENTOS_CONTEO_DIRECTO
    )


def usar_valor_anterior_real(mov):

    mov = norm(mov)

    return mov in MOVIMIENTOS_RESETEO_VALOR_ANTERIOR


def usar_nuevo_valor_directo(mov):

    mov = norm(mov)

    return mov in MOVIMIENTOS_RESETEO_NUEVO_VALOR


# =========================================================
# CALCULAR DIFERENCIA
# =========================================================

def calcular_diferencia(evento):

    va = to_float(evento.get("valor_anterior"))
    nv = to_float(evento.get("nuevo_valor"))

    if va is None or nv is None:
        return None

    return nv - va



# =========================================================
# RECONSTRUIR PRODUCTO
# =========================================================

def reconstruir_producto(conn, codigo_producto, fecha_inicio, fecha_fin=None):
    historial = obtener_eventos(codigo_producto, fecha_inicio, fecha_fin)
    historial.sort(
        key=lambda x: (
            parse_fecha(x.get("fecha")),
            PRIORIDAD_MOVIMIENTO.get(
                norm(x.get("movimiento")),
                999
            )
        )
    )

    stock_actual = 0.0
    print(f"[RECONSTRUIR INICIO] {codigo_producto} | fecha_inicio={fecha_inicio} | eventos={len(historial)}")
    reconstruido = []
    
    for e in historial:

        mov = norm(e.get("movimiento"))

        va_original = to_float(e.get("valor_anterior"))
        nv_original = to_float(e.get("nuevo_valor"))
        cantidad = to_float(e.get("cantidad"))

        if mov == "carga de facturas (historial)":
            print(
                "[CARGA FACTURA]",
                "fecha=", e.get("fecha"),
                "va_original=", va_original,
                "nv_original=", nv_original,
                "stock_actual=", stock_actual
            )

        # =====================================================
        # EVENTOS AUXILIARES + RESETEOS
        # =====================================================

        if es_movimiento_reseteo(mov):

            anterior = stock_actual

            # -------------------------------------------------
            # CARGA FACTURA HISTORIAL
            # SOLO VISUAL
            # NO MODIFICA STOCK REAL
            # -------------------------------------------------

            if mov == "carga de facturas (historial)":
                impacto = (nv_original or 0) - (va_original or 0)
                anterior = stock_actual
                nuevo = stock_actual + impacto

                # IMPORTANTE:
                # stock_actual NO cambia

            # -------------------------------------------------
            # FACTURAS DETALLADAS
            # ESTE SÍ ES EL MOVIMIENTO REAL
            # -------------------------------------------------

            elif mov == "facturas detalladas":

                impacto = cantidad if cantidad is not None else 0

                anterior = stock_actual
                nuevo = stock_actual + impacto

                # ESTE SÍ modifica stock_actual luego

            # -------------------------------------------------
            # RESETEOS REALES
            # -------------------------------------------------

            else:

                if mov in MOVIMIENTOS_CONTEO_DIRECTO:
                    print(f"[CONTEO] fecha={e.get('fecha')} cantidad={cantidad} stock_antes={stock_actual}")
                    anterior = stock_actual
                    nuevo = cantidad if cantidad is not None else stock_actual

                elif (
                    usar_valor_anterior_real(mov)
                    and va_original is not None
                ):
                    anterior = va_original
                    if usar_nuevo_valor_directo(mov) and nv_original is not None:
                        nuevo = nv_original
                    else:
                        nuevo = stock_actual if cantidad is None else stock_actual + cantidad

                elif usar_nuevo_valor_directo(mov) and nv_original is not None:
                    nuevo = nv_original

                else:
                    nuevo = stock_actual if cantidad is None else stock_actual + cantidad

                if nuevo is None:
                    nuevo = stock_actual

        # =====================================================
        # MOVIMIENTOS NORMALES
        # =====================================================

        else:

            diferencia = calcular_diferencia(e)
            anterior = stock_actual
            if diferencia is None:
                if cantidad is not None:
                    if mov in MOVIMIENTOS_SUMA:
                        diferencia = cantidad
                    elif mov in MOVIMIENTOS_RESTA:
                        diferencia = cantidad  # cantidad ya viene negativa desde b_loader_movimientos
                    else:
                        diferencia = 0
                else:
                    diferencia = 0
            nuevo = stock_actual + diferencia

        # =====================================================
        # NORMALIZAR
        # =====================================================

        anterior = round_safe(anterior)
        nuevo = round_safe(nuevo)

        nuevo_evento = deepcopy(e)

        nuevo_evento["stock_reconstruido"] = nuevo
        nuevo_evento["valor_anterior_reconstruido"] = anterior
        nuevo_evento["nuevo_valor_reconstruido"] = nuevo

        reconstruido.append(nuevo_evento)

        # =====================================================
        # SOLO EVENTOS REALES MODIFICAN STOCK
        # =====================================================

        if mov != "carga de facturas (historial)":
            stock_actual = nuevo

    return {
        "codigo": codigo_producto,
        "total_movimientos": len(reconstruido),
        "historial": reconstruido,
        "stock_final": (
            reconstruido[-1]["stock_reconstruido"]
            if reconstruido
            else 0
        )
    }


# =========================================================
# RECONSTRUIR MUCHOS PRODUCTOS
# =========================================================

def reconstruir_productos(codigos):

    resultados = {}

    for codigo in codigos:

        try:

            resultados[codigo] = (
                reconstruir_producto(None, codigo, FECHA_INICIO_DEFAULT)
            )

        except Exception as e:

            resultados[codigo] = {
                "error": str(e)
            }

    return resultados


# =========================================================
# API SIMPLE
# =========================================================

def ejecutar_reconstruccion(codigo):

    return reconstruir_producto(None, codigo, FECHA_INICIO_DEFAULT)

