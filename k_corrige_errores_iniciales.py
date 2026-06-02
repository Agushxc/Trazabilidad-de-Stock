# k_corrige_errores_iniciales.py
from datetime import datetime

from a_00_config import *
from a_db import *
from b_loader_movimientos import obtener_eventos
from c_motor_trazabilidad import reconstruir_stock
from d_analizador_errores import ejecutar_analisis
from datetime import datetime, timedelta

# =========================================================
# UTILIDADES
# =========================================================

def to_float(x):
    try:
        return float(x)
    except:
        return None

def parse_fecha(x):
    if not x:
        return None

    formatos=[
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%d-%m %H:%M:%S"
    ]

    for f in formatos:
        try:
            return datetime.strptime(str(x),f)
        except:
            pass

    return None

def fecha_media(f1,f2):
    if not f1 or not f2:
        return None
    return f1+(f2-f1)/2

def fmt_fecha(x):
    if not x:
        return None
    return x.strftime("%Y-%m-%d %H:%M:%S")

# =========================================================
# AJUSTE DE ORDEN TEMPORAL (FIX CRÍTICO)
# =========================================================

def normalizar_tiempo_conteos(historial):
    for i in range(len(historial) - 1):
        actual = historial[i]
        siguiente = historial[i + 1]
        mov_a = str(actual.get("movimiento", "")).strip().lower()
        mov_b = str(siguiente.get("movimiento", "")).strip().lower()
        fecha_a = parse_fecha(actual.get("fecha"))
        fecha_b = parse_fecha(siguiente.get("fecha"))
        if not fecha_a or not fecha_b:
            continue
        if (
            mov_a == "conteo de stock" and
            mov_b == "conteo de stock (historial)" and
            fecha_a <= fecha_b and
            (fecha_b - fecha_a).total_seconds() <= 60
        ):
            nueva_fecha = fecha_a - timedelta(seconds=1)
            db.ejecutar("""
                UPDATE historial_de_articulos
                SET fecha_y_hora_de_modificacion = ?
                WHERE fecha_y_hora_de_modificacion = ?
                AND LOWER(TRIM(desde)) = 'conteo de stock'
            """, (
                fmt_fecha(nueva_fecha),
                siguiente.get("fecha")
            ))

# =========================================================
# OBTENER DESCRIPCIÓN
# =========================================================

def obtener_descripcion(codigo):
    row = db.ejecutar_uno(
        "SELECT descripcion FROM productos WHERE codigo=?",
        (codigo,)
    )
    return row["descripcion"] if row else ""


# =========================================================
# INSERTAR AJUSTE INVENTADO
# =========================================================

def insertar_ajuste(codigo,descripcion,valor_anterior,nuevo_valor,fecha):

    db.ejecutar("""
    INSERT INTO historial_de_articulos(
        codigo,
        descripcion,
        tipo_de_modificacion,
        valor_anterior,
        nuevo_valor,
        usuario_responsable,
        comentario,
        fecha_y_hora_de_modificacion,
        desde
    )
    VALUES(?,?,?,?,?,?,?,?,?)
    """,(
        codigo,
        descripcion,
        "stock_actual",
        valor_anterior,
        nuevo_valor,
        "Agu",
        "automático al obtener trazabilidad de stock. Esto es porque se corrigió el stock pero no se registró el cambio, mala práctica antigua",
        fecha,
        "Ajuste manual con auditoría inventada"
    ))

# =========================================================
# GENERAR CORRECCIONES
# =========================================================
def generar_correcciones(codigo,historial,inconsistencias):
    correcciones=[]
    for e in inconsistencias:
        idx=e.get("indice")

        if idx is None or idx<=0 or idx>=len(historial):
            continue

        actual=historial[idx]
        previo=historial[idx-1]

        fecha_prev=parse_fecha(previo.get("fecha"))
        fecha_act=parse_fecha(actual.get("fecha"))

        fecha_corr=fecha_media(fecha_prev,fecha_act)

        esperado=to_float(previo.get("stock_reconstruido"))
        encontrado=to_float(actual.get("valor_anterior"))

        if esperado is None or encontrado is None:
            continue

        delta=encontrado-esperado

        correcciones.append({
            "codigo":codigo,
            "fecha":fmt_fecha(fecha_corr),
            "fecha_original":actual.get("fecha"),
            "delta":delta,
            "valor_anterior":esperado,
            "nuevo_valor":encontrado,
            "movimiento": actual.get("movimiento")
        })

    return correcciones

# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def corregir_errores_iniciales(codigo):
    print("\n"+"="*70)
    print(f"CÓDIGO: {codigo}")
    print("="*70)

    movimientos=obtener_eventos(codigo)

    if not movimientos:
        print("No hay movimientos.")
        return
    
    # FIX DE ORDEN TEMPORAL
    normalizar_tiempo_conteos(movimientos)
    db.commit()

    # Recargar después de normalizar
    movimientos=obtener_eventos(codigo)
    historial=reconstruir_stock(codigo)

    resultado=ejecutar_analisis(historial)

    inconsistencias=resultado["inconsistencias"]
    print("\nInconsistencias detectadas por el corrector:")
    for inc in inconsistencias:
        print(inc.get("indice"), inc.get("detalle", {}).get("fecha"), inc.get("detalle", {}).get("movimiento"))
    
    print(f"\nInconsistencias antes: {len(inconsistencias)}")

    if not inconsistencias:
        print("No hay inconsistencias para corregir.")
        return

    descripcion=obtener_descripcion(codigo)

    correcciones=generar_correcciones(codigo,historial,inconsistencias)

    if not correcciones:
        print("No se pudieron generar correcciones.")
        return

    print("\nCorrecciones generadas:\n")

    for c in correcciones:
        print(
            f'{c["fecha"]} | {c["movimiento"]} | '
            f'{c["delta"]} | {c["valor_anterior"]} -> {c["nuevo_valor"]}'
        )
    print("\nAplicando correcciones...\n")


    for c in correcciones:

        idx=None



        for e in inconsistencias:

            detalle=e.get("detalle",{})

            fecha=detalle.get("fecha")
            mov=detalle.get("movimiento")

            if fecha==c["fecha_original"] and mov.strip().lower()==c["movimiento"].strip().lower():
                idx=e["indice"]
                break
        if idx is None:
            continue

        actual=historial[idx]

        mov=actual.get("movimiento","").strip().lower()

        # =====================================================
        # CASO ESPECIAL:
        # CARGA DE FACTURAS
        # =====================================================

        if mov=="carga de facturas (historial)":

            esperado=c["valor_anterior"]

            nuevo=esperado

            j=idx+1

            while j<len(historial):

                sig=historial[j]

                mov_sig=sig.get("movimiento","").strip().lower()

                if mov_sig=="facturas detalladas":

                    cant=to_float(sig.get("cantidad"))

                    if cant is not None:
                        nuevo+=cant

                    j+=1
                    continue

                break

            db.ejecutar("""
            UPDATE historial_de_articulos
            SET
                valor_anterior=?,
                nuevo_valor=?
            WHERE datetime(fecha_y_hora_de_modificacion)=datetime(?)
            AND LOWER(TRIM(desde))='carga de facturas'
            AND tipo_de_modificacion = "Stock Actual"
            """,(
                esperado,
                nuevo,
                actual.get("fecha")
            ))

            print(
                f'UPDATE carga factura: '
                f'{esperado} -> {nuevo}'
            )
        elif mov == "corrección manual antes de cargar factura (historial)":
            db.ejecutar("""
                UPDATE historial_de_articulos
                SET valor_anterior = ?
                WHERE datetime(fecha_y_hora_de_modificacion) = datetime(?)
                AND LOWER(TRIM(desde)) = 'corrección manual antes de cargar factura'
                AND tipo_de_modificacion = 'Stock Actual'
            """, (
                c["valor_anterior"],
                actual.get("fecha")
            ))
            print(f'UPDATE corrección manual: {c["valor_anterior"]} -> {actual.get("nuevo_valor")}')
        elif mov == "conteo de stock (historial)":
            db.ejecutar("""
                UPDATE historial_de_articulos
                SET valor_anterior = ?
                WHERE datetime(fecha_y_hora_de_modificacion) = datetime(?)
                AND LOWER(TRIM(desde)) = 'conteo de stock'
                AND codigo = ?
            """, (
                c["valor_anterior"],
                actual.get("fecha"),
                codigo
            ))
            print(f'UPDATE conteo stock: {c["valor_anterior"]} -> {actual.get("nuevo_valor")}')
        # =====================================================
        # RESTO
        # =====================================================

        else:

            insertar_ajuste(
                codigo=codigo,
                descripcion=descripcion,
                valor_anterior=c["valor_anterior"],
                nuevo_valor=c["nuevo_valor"],
                fecha=c["fecha"]
            )
            print(
                f'INSERT ajuste inventado: '
                f'{c["valor_anterior"]} -> {c["nuevo_valor"]} | fecha: {c["fecha"]}'
            )

    db.commit()
    db.cerrar()

    print("Correcciones aplicadas.")

    # Revalidar
    movimientos2=obtener_eventos(codigo)
    historial2=reconstruir_stock(codigo)

    resultado2=ejecutar_analisis(historial2)

    inconsistencias_restantes=resultado2["inconsistencias"]

    print(f"\nInconsistencias después: {len(inconsistencias_restantes)}")

    if inconsistencias_restantes:
        print("\nSiguen existiendo inconsistencias:")
        for e in inconsistencias_restantes:
            print(e)
    return len(inconsistencias_restantes)

if __name__=="__main__":
    cod=input("Código: ").strip()
    corregir_errores_iniciales(cod)