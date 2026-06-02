# f_aplicador_cambios
import sqlite3
from datetime import datetime, timedelta
from a_db import db
from j_reconstructor import reconstruir_producto
#from h_validadores import validar_sistema_post_cambio
import traceback
from a_00_config import *

# UTILIDADES BASE
def parse_dt(s: str) -> datetime:
    return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S")

def fmt_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def reconstruir_y_persistir_historial(conn, codigo_producto, fecha_inicio, ts_old_str):

    reconstruido = reconstruir_producto(
        conn,
        codigo_producto,
        fecha_inicio
    )

    historial = reconstruido.get("historial", [])

    c = conn.cursor()

    print(f"[RECONSTRUIR] {codigo_producto} | eventos={len(historial)}")
    
    if str(codigo_producto) == "114":
        print("\n================ TRACE 114 ================\n")
    for ev in historial:

        fecha = (
            ev.get("fecha_y_hora_de_modificacion")
            or ev.get("fecha")
        )
        if fecha > ts_old_str:
            continue
        #print(f"[UPDATE HIST] {codigo_producto} | {fecha}")

        #movimiento = ev.get("movimiento")
        if str(codigo_producto) == "114":
            print(
                "[TRACE 114]",
                "fecha:", fecha,
                "| mov:", ev.get("movimiento"),
                "| stock_calc:", ev.get("stock_reconstruido"),
                "| va_calc:", ev.get("valor_anterior_reconstruido"),
                "| nv_calc:", ev.get("nuevo_valor_reconstruido")
            )
        valor_anterior = ev.get("valor_anterior_reconstruido")
        nuevo_valor = ev.get("nuevo_valor_reconstruido")


        if str(codigo_producto) == "114":
            print(
                "[TRACE 114 -> DB UPDATE]",
                "fecha:", fecha,
                "valor_anterior_final:", float(valor_anterior),
                "nuevo_valor_final:", float(nuevo_valor)
            )
        c.execute("""
            UPDATE historial_de_articulos
            SET valor_anterior = ?,
                nuevo_valor = ?
            WHERE codigo = ?
            AND fecha_y_hora_de_modificacion = ?
        """, (
            float(valor_anterior),
            float(nuevo_valor),
            str(codigo_producto),
            fecha
        ))

# ACTUALIZACIÓN DE STOCK FINAL
def actualizar_stock_actual_desde_historial(conn, codigo_producto):
    reconstruido = reconstruir_producto(conn, codigo_producto, FECHA_INICIO_DEFAULT)
    if not reconstruido:
        return

    ultimo_stock = reconstruido["stock_final"]

    c = conn.cursor()
    c.execute("""
        UPDATE productos
        SET stock_actual = ?
        WHERE codigo = ?
    """, (float(ultimo_stock), str(codigo_producto)))

# APLICADOR PRINCIPAL
def aplicar_cambios(cambios):
    for cng in cambios:
        if cng.get("tipo") != "mover_factura":
            continue
        factura_id = cng.get("id_factura")
        ts_nueva_str = cng.get("fecha_sugerida")
        if factura_id is None or ts_nueva_str is None:
            continue
        print(f"[APLICAR] factura={factura_id} → {ts_nueva_str}")

        conn = db.conectar()
        c = db.cursor

        try:
            # -------------------------------------------------
            # 1. TRAER FACTURA ORIGINAL
            # -------------------------------------------------
            c.execute("""
                SELECT fecha_y_hora_de_compra, nombre_proveedor
                FROM facturas_resumidas
                WHERE id_factura = ?
            """, (factura_id,))

            row = c.fetchone()
            if not row:
                print(f"[ERROR] factura {factura_id} no existe")
                continue

            ts_old_str, proveedor = row
            ts_old = parse_dt(ts_old_str)
            ts_new = parse_dt(ts_nueva_str)

            offset = ts_new - ts_old

            # -------------------------------------------------
            # 2. TRAER DETALLES
            # -------------------------------------------------
            c.execute("""
                SELECT id_detalle, fecha_y_hora_agregado, codigo_producto, cantidad
                FROM facturas_detalladas
                WHERE id_factura = ?
            """, (factura_id,))

            detalles = c.fetchall()

            detalles_movidos = []

            # -------------------------------------------------
            # 3. MOVER DETALLES
            # -------------------------------------------------
            for id_detalle, ts_det_str, codigo, cantidad in detalles:

                ts_det = parse_dt(ts_det_str)
                ts_det_nueva = ts_det + offset
                ts_det_nueva_str = fmt_dt(ts_det_nueva)

                detalles_movidos.append({
                    "codigo": str(codigo),
                    "cantidad": float(cantidad or 0),
                    "ts_original": ts_det_str,
                    "ts_nueva": ts_det_nueva_str
                })

                # actualizar detalle
                c.execute("""
                    UPDATE facturas_detalladas
                    SET fecha_y_hora_agregado = ?
                    WHERE id_detalle = ?
                """, (ts_det_nueva_str, id_detalle))

                # actualizar historial asociado
                c.execute("""
                    UPDATE historial_de_articulos
                    SET fecha_y_hora_de_modificacion = ?
                    WHERE codigo = ?
                    AND fecha_y_hora_de_modificacion = ?
                    AND desde = 'Carga de facturas'
                """, (ts_det_nueva_str, str(codigo), ts_det_str))

                # sincronizar facturas_resumidas
                c.execute("""
                    UPDATE facturas_resumidas
                    SET fecha_y_hora_de_compra = ?
                    WHERE id_factura = ?
                """, (ts_nueva_str, factura_id))

            # -------------------------------------------------
            # 4. RECONSTRUCCIÓN + AJUSTE GLOBAL
            # -------------------------------------------------
            codigos_afectados = set()

            for d in detalles_movidos:
                codigos_afectados.add(str(d["codigo"]))

            for codigo_afectado in codigos_afectados:
                fecha_inicio_reconstruccion = min(
                    [d["ts_original"]
                        for d in detalles_movidos
                        if str(d["codigo"]) == str(codigo_afectado)] +
                    [d["ts_nueva"]
                        for d in detalles_movidos
                        if str(d["codigo"]) == str(codigo_afectado)]
                )

                print(
                    f"[INICIO RECONSTRUCCIÓN] "
                    f"{codigo_afectado} "
                    f"desde {fecha_inicio_reconstruccion}"
                )

                reconstruir_y_persistir_historial(
                    conn,
                    codigo_afectado,
                    FECHA_INICIO_DEFAULT,
                    ts_old_str
                )
                actualizar_stock_actual_desde_historial(
                    conn,
                    codigo_afectado
                )

                print(f"[FIN RECONSTRUCCIÓN] {codigo_afectado}")


            # -------------------------------------------------
            # 5. VALIDACIÓN + RECONSTRUCCIÓN GLOBAL
            # -------------------------------------------------
            
            #for d in detalles_movidos:
                #validar_sistema_post_cambio(conn, d["codigo"])



            db.commit()
            print(f"[OK] Factura {factura_id} actualizada")

        except Exception as e:
            conn.rollback()
            print(f"[ERROR] id de factura:  {factura_id}")
            traceback.print_exc()
