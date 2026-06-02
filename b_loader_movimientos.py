# b_loader_movimientos.py
from datetime import datetime
from a_db import db
from a_00_config import *

TIPOS_STOCK = [
    "stock actual",
    "stock_actual",
    "cantidad",
    "cambio de stock"
]

# UTILIDAD FECHA
def parse_fecha(fecha):
    if not fecha:
        return None

    try:
        return datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
    except:
        return None


# CARGA UNIFICADA DE EVENTOS
def cargar_eventos(codigo_producto, fecha_inicio=FECHA_INICIO_DEFAULT, fecha_fin=None):
    db.conectar()
    eventos = []

    # HISTORIAL STOCK
    historial = db.ejecutar("""
        SELECT 
            fecha_y_hora_de_modificacion,
            desde,
            valor_anterior,
            nuevo_valor
        FROM historial_de_articulos
        WHERE codigo = ?
        AND datetime(fecha_y_hora_de_modificacion) >= datetime(?)
        AND (
            LOWER(TRIM(tipo_de_modificacion)) LIKE '%stock actual%' OR
            LOWER(TRIM(tipo_de_modificacion)) LIKE '%stock_actual%' OR
            LOWER(TRIM(tipo_de_modificacion)) LIKE '%cantidad%' OR
            LOWER(TRIM(tipo_de_modificacion)) LIKE '%cambio de stock%'
        )
    """, (codigo_producto, fecha_inicio))

    for r in historial:
        eventos.append({
            "fecha": r["fecha_y_hora_de_modificacion"],
            "tipo": "historial",
            "movimiento": f"{r['desde'] or 'EN HISTORIAL NO DICE DESDE DONDE'} (historial)",
            "valor_anterior": r["valor_anterior"],
            "nuevo_valor": r["nuevo_valor"],
            "cantidad": None,
            "id_factura": None,
            "fecha_carga": None,
            "fecha_compra": None
        })

    # FACTURAS DETALLADAS
    facturas_det = db.ejecutar("""
        SELECT 
            fecha_y_hora_agregado,
            cantidad,
            id_factura
        FROM facturas_detalladas
        WHERE codigo_producto = ?
        AND datetime(fecha_y_hora_agregado) >= datetime(?)
    """, (codigo_producto, fecha_inicio))

    for r in facturas_det:
        eventos.append({
            "fecha": r["fecha_y_hora_agregado"],
            "tipo": "compra",
            "movimiento": "facturas detalladas",
            "valor_anterior": None,
            "nuevo_valor": None,
            "cantidad": float(r["cantidad"] or 0),
            "id_factura": r["id_factura"],
            "fecha_carga": None,
            "fecha_compra": None
        })

    # FACTURAS RESUMIDAS
    facturas_res = db.ejecutar("""
        SELECT DISTINCT
            fr.id_factura,
            fr.fecha_y_hora_de_carga,
            fr.fecha_y_hora_de_compra
        FROM facturas_resumidas fr
        JOIN facturas_detalladas fd
            ON fd.id_factura = fr.id_factura
        WHERE fd.codigo_producto = ?
        AND (
            datetime(fr.fecha_y_hora_de_compra) >= datetime(?)
            OR datetime(fr.fecha_y_hora_de_carga) >= datetime(?)
        )
    """, (codigo_producto, fecha_inicio, fecha_inicio))

    for r in facturas_res:
        eventos.append({
            "fecha": r["fecha_y_hora_de_compra"],
            "tipo": "factura_resumida",
            "movimiento": "facturas resumidas",
            "valor_anterior": None,
            "nuevo_valor": None,
            "cantidad": None,
            "id_factura": r["id_factura"],
            "fecha_carga": r["fecha_y_hora_de_carga"],
            "fecha_compra": r["fecha_y_hora_de_compra"]
        })

    # CONTEO STOCK
    conteos = db.ejecutar("""
        SELECT fecha_hora, cantidad_contada
        FROM conteo_de_stock
        WHERE codigo_producto = ?
        AND datetime(fecha_hora) >= datetime(?)
    """, (codigo_producto, fecha_inicio))

    for r in conteos:
        eventos.append({
            "fecha": r["fecha_hora"],
            "tipo": "conteo",
            "movimiento": "conteo de stock",
            "valor_anterior": None,
            "nuevo_valor": None,
            "cantidad": float(r["cantidad_contada"] or 0),
            "id_factura": None,
            "fecha_carga": None,
            "fecha_compra": None
        })

    PROMOS = db.ejecutar("""
        SELECT 
            id_promocion,
            cantidad_en_promo
        FROM promociones
        WHERE codigo = ?
    """, (codigo_producto,))

    MAPA_PROMOS = {}

    for p in PROMOS:
        MAPA_PROMOS[p["id_promocion"]] = float(p["cantidad_en_promo"] or 0)

    # VENTAS
    ventas = db.ejecutar("""
        SELECT 
            vr.fecha_hora,
            vd.cantidad,
            vd.id_venta,
            vd.codigo_producto
        FROM ventas_detalladas vd
        INNER JOIN ventas_resumidas vr
            ON vr.id_venta = vd.id_venta
        WHERE (
            vd.codigo_producto = ?
            OR vd.codigo_producto IN (
                SELECT id_promocion
                FROM promociones
                WHERE codigo = ?
            )
        )
        AND datetime(vr.fecha_hora) >= datetime(?)
    """, (codigo_producto, codigo_producto, fecha_inicio))

    for r in ventas:

        codigo_venta = r["codigo_producto"]
        cantidad = float(r["cantidad"] or 0)

        # VENTA NORMAL
        if codigo_venta == codigo_producto:

            cantidad_final = -cantidad

        # VENTA POR PROMOCIÓN
        elif codigo_venta in MAPA_PROMOS:

            cantidad_final = -(cantidad * MAPA_PROMOS[codigo_venta])

        else:
            continue

        eventos.append({
            "fecha": r["fecha_hora"],
            "tipo": "venta",
            "movimiento": "ventas detalladas",
            "valor_anterior": None,
            "nuevo_valor": None,
            "cantidad": cantidad_final,
            "id_factura": None,
            "fecha_carga": None,
            "fecha_compra": None
        })

    # ORDENAR EVENTOS
    eventos.sort(
        key=lambda x: (
            parse_fecha(x["fecha"]) or datetime.min,
            PRIORIDAD_MOVIMIENTO.get(x["tipo"], 999)
        )
    )

    return eventos

# WRAPPER SIMPLE (API LIMPIA)
def obtener_eventos(codigo_producto, fecha_inicio=FECHA_INICIO_DEFAULT, fecha_fin=None):
    return cargar_eventos(codigo_producto, fecha_inicio, fecha_fin)