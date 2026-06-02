# c_motor_trazabilidad.py
from copy import deepcopy
from datetime import datetime
from b_loader_movimientos import obtener_eventos
from a_00_config import *
from a_db import *

# PARSEO FECHA
def parse_fecha(fecha):
    try:
        return datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
    except:
        return datetime.min

def norm(m):
    return m.strip().lower() if isinstance(m, str) else m

# STOCK BASE INICIAL
def consigue_stock_base_y_inicio(eventos):
    if not eventos:
        return 0, 0

    acumulado_ventas = 0

    for i, e in enumerate(eventos):
        mov = norm(e.get("movimiento"))

        # ignorar explícitamente
        if mov in MOVIMIENTOS_IGNORE:
            continue

        # ventas restan base
        if mov in MOVIMIENTOS_RESTA:
            if e.get("cantidad") not in (None, ""):
                try:
                    acumulado_ventas += abs(float(e["cantidad"]))
                    #print(f"venta: cant {abs(float(e['cantidad']))} acumulado {acumulado_ventas}")
                except:
                    pass

        # facturas suman base (si aparecen antes del corte real)
        elif mov in MOVIMIENTOS_SUMA:
            pass

        # conteo directo
        elif mov in MOVIMIENTOS_CONTEO_DIRECTO:
            raw = e.get("cantidad")
            if raw not in (None, ""):
                try:
                    base = float(raw)
                    return base + acumulado_ventas, i + 1
                except:
                    pass

        # resets valor anterior
        elif mov in MOVIMIENTOS_RESETEO_VALOR_ANTERIOR:
            raw = e.get("valor_anterior")
            if raw not in (None, ""):
                try:
                    return float(raw) + acumulado_ventas, i + 1
                except:
                    pass

        # resets nuevo valor
        elif mov in MOVIMIENTOS_RESETEO_NUEVO_VALOR:
            raw = e.get("nuevo_valor")
            if raw not in (None, ""):
                try:
                    return float(raw), i + 1
                except:
                    pass


    return acumulado_ventas, 0

# MOTOR PRINCIPAL
def reconstruir_stock(codigo_producto, fecha_inicio=FECHA_INICIO_DEFAULT):
    eventos = obtener_eventos(codigo_producto, fecha_inicio)
    eventos = deepcopy(eventos)

    stock_base, _ = consigue_stock_base_y_inicio(eventos)
    stock = float(stock_base)

    historial_stock = []

    for e in eventos:
        mov = norm(e.get("movimiento"))
        cant = e.get("cantidad")
        try:
            cant = float(cant) if cant is not None else None
        except:
            cant = None

        if mov in MOVIMIENTOS_RESETEO:
            if e.get("nuevo_valor") not in (None, ""):
                try:
                    stock = float(e["nuevo_valor"])
                except:
                    pass

        elif mov in MOVIMIENTOS_CONTEO_DIRECTO:
            if cant is not None:
                stock = cant

        elif mov in MOVIMIENTOS_RESTA:
            if cant is not None:
                stock += cant

        elif mov in MOVIMIENTOS_SUMA:
            if cant is not None:
                stock += cant

        e["stock_reconstruido"] = round(stock, 6)
        e["comentario"] = e.get("comentario")
        e["fecha_carga"] = e.get("fecha_carga")
        e["fecha_compra"] = e.get("fecha_compra")

        historial_stock.append(e)

    return historial_stock

# DETECCIÓN SIMPLE DE ERRORES
def detectar_inconsistencias(historial):
    errores = []

    for i in range(1, len(historial)):
        actual = historial[i]
        anterior = historial[i - 1]

        a = actual.get("stock_reconstruido")
        b = anterior.get("stock_reconstruido")

        try:
            if a is not None and b is not None:
                if abs(a - b) > SALTO_MAXIMO_PERMITIDO:
                    errores.append(actual)
        except:
            continue

    return errores

# API PRINCIPAL DEL MOTOR
def analizar(codigo_producto, fecha_inicio=FECHA_INICIO_DEFAULT):
    historial = reconstruir_stock(codigo_producto, fecha_inicio)
    errores = detectar_inconsistencias(historial)
    return {
        "historial": historial,
        "errores": errores
    }