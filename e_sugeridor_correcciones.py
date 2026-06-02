# e_sugeridor_correcciones.py
from copy import deepcopy
from datetime import datetime
from a_00_config import *

# UTILIDAD
def parse_fecha(fecha):
    try:
        return datetime.strptime(
            fecha,
            "%Y-%m-%d %H:%M:%S"
        )
    except:
        return None

def norm(x):
    return x.strip().lower() if isinstance(x, str) else x

def to_float(x):
    try:
        if x in (None, ""):
            return None

        return float(x)

    except:
        return None


# DETECTAR TRAMOS NEGATIVOS
def detectar_tramos_negativos(historial):

    tramos = []

    inicio = None

    for i, e in enumerate(historial):

        stock = to_float(
            e.get("stock_reconstruido")
        )

        if stock is None:
            continue

        # ENTRA EN NEGATIVO
        if (
            stock < UMBRAL_NEGATIVO
            and inicio is None
        ):
            inicio = i

        # SALE DEL NEGATIVO
        elif (
            stock >= TOLERANCIA_CERO
            and inicio is not None
        ):
            tramos.append((inicio, i - 1))
            inicio = None

    # TERMINA NEGATIVO
    if inicio is not None:

        tramos.append((
            inicio,
            len(historial) - 1
        ))

    return tramos


# BUSCAR ÚLTIMO STOCK POSITIVO
def buscar_ultimo_positivo(historial, idx_inicio):

    for i in range(idx_inicio - 1, -1, -1):

        stock = to_float(
            historial[i].get("stock_reconstruido")
        )

        if stock is None:
            continue

        if stock >= TOLERANCIA_CERO:
            return {
                "indice": i,
                "fecha": historial[i].get("fecha"),
                "stock": stock,
                "evento": historial[i]
            }

    return {
        "indice": 0,
        "fecha": None,
        "stock": None,
        "evento": None
    }



# ES MOVIMIENTO QUE AGREGA STOCK
def es_movimiento_entrada(mov):
    mov = norm(mov)
    return mov in [
        "facturas detalladas"
    ]


# GENERAR SUGERENCIAS
def sugerir_correcciones(historial):

    historial = deepcopy(historial)

    sugerencias = []

    tramos = detectar_tramos_negativos(
        historial
    )

    for inicio, fin in tramos:

        evento_inicio = historial[inicio]

        fecha_inicio_negativo = (
            evento_inicio.get("fecha")
        )

        fecha_inicio_dt = parse_fecha(
            fecha_inicio_negativo
        )

        info_positivo = buscar_ultimo_positivo(
            historial,
            inicio
        )

        fecha_anterior_positivo = (
            info_positivo["fecha"]
        )

        fecha_anterior_dt = parse_fecha(
            fecha_anterior_positivo
        )

        stock_positivo = (
            info_positivo["stock"]
        )

        stock_virtual = to_float(
            evento_inicio.get(
                "stock_reconstruido"
            )
        )

        if stock_virtual is None:
            continue

        sugerencia_generada = False

        # RECORRER FUTURO
        for k in range(
            inicio + 1,
            len(historial)
        ):

            fut = historial[k]

            mov = norm(fut.get("movimiento"))
            id_factura = fut.get("id_factura")

            if mov == "facturas detalladas" and id_factura is None:
                continue

            # RESETS CORTAN
            if (
                mov in MOVIMIENTOS_RESETEO
                or mov in MOVIMIENTOS_CONTEO_DIRECTO
            ):
                break

            # VENTAS FUTURAS
            if mov == "ventas detalladas":

                cant = to_float(
                    fut.get("cantidad")
                )

                if cant is not None:
                    stock_virtual += cant

            # ENTRADAS FUTURAS
            elif es_movimiento_entrada(mov):

                cantidad_entrada = None

                # FACTURA
                if mov == "facturas detalladas":

                    cantidad_entrada = to_float(
                        fut.get("cantidad")
                    )

                # HISTORIAL / CONTEO
                else:

                    nuevo_valor = to_float(
                        fut.get("nuevo_valor")
                    )

                    valor_anterior = to_float(
                        fut.get("valor_anterior")
                    )

                    if (
                        nuevo_valor is not None
                        and valor_anterior is not None
                    ):
                        cantidad_entrada = (
                            nuevo_valor
                            - valor_anterior
                        )

                if cantidad_entrada is None:
                    continue

                if cantidad_entrada is not None:
                    stock_virtual += cantidad_entrada

                # SIGUE NEGATIVO
                if stock_virtual < TOLERANCIA_CERO:
                    continue

                # FECHA EVENTO
                fecha_evento = fut.get("fecha")

                fecha_evento_dt = parse_fecha(
                    fecha_evento
                )

                # VALIDAR TOLERANCIA DÍAS
                if (fecha_inicio_dt and fecha_evento_dt and abs((fecha_evento_dt - fecha_inicio_dt).days) > DIAS_TOLERANCIA_FACTURA):
                    continue

                # FECHA SUGERIDA
                if (fecha_anterior_dt and fecha_inicio_dt):
                    from datetime import timedelta
                    sugerida = fecha_inicio_dt - timedelta(minutes=2)
                    fecha_sugerida = (sugerida.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    fecha_sugerida = (fecha_inicio_negativo)

                # TIPO SUGERENCIA
                if mov == "facturas detalladas":
                    sugerencias.append({
                        "tipo": "mover_factura",
                        "id_factura": fut.get("id_factura") if fut.get("id_factura") is not None else None,
                        "cantidad":
                            fut.get("cantidad"),
                        "fecha_original":
                            fecha_evento,
                        "fecha_sugerida":
                            fecha_sugerida,
                        "fecha_inicio_negativo":
                            fecha_inicio_negativo,
                        "fecha_anterior_positivo":
                            fecha_anterior_positivo,
                        "stock_positivo":
                            stock_positivo,
                        "stock_negativo":
                            evento_inicio.get("stock_reconstruido"),
                        "sugerencia":
                            "Mover factura antes del tramo negativo",
                        "prioridad":
                            "alta"})

                else:

                    sugerencias.append({

                        "tipo":
                            "ajuste_requerido",

                        "movimiento":
                            fut.get("movimiento"),

                        "fecha_evento":
                            fecha_evento,

                        "id_factura":
                            fut.get("id_factura"),
                            
                        "fecha_sugerida":
                            fecha_sugerida,

                        "fecha_inicio_negativo":
                            fecha_inicio_negativo,

                        "fecha_anterior_positivo":
                            fecha_anterior_positivo,

                        "stock_positivo":
                            stock_positivo,

                        "stock_negativo":
                            evento_inicio.get("stock_reconstruido"),

                        "valor_anterior":
                            fut.get("valor_anterior"),

                        "nuevo_valor":
                            fut.get("nuevo_valor"),

                        "stock_virtual_antes":
                            (stock_virtual - cantidad_entrada) if cantidad_entrada is not None else None,
                        "stock_virtual_despues":
                            stock_virtual,

                        # "sugerencia":
                        #     "El stock requiere ajuste en la fecha del movimiento",

                        "prioridad":
                            "alta"
                    })

                sugerencia_generada = True
                break

        # NO SE ENCONTRÓ NADA
        if not sugerencia_generada:

            sugerencias.append({

                "tipo":
                    "revision_manual",

                "fecha_inicio_negativo":
                    fecha_inicio_negativo,

                "fecha_anterior_positivo":
                    fecha_anterior_positivo,

                "stock_positivo":
                    stock_positivo,

                "stock_negativo":
                    evento_inicio.get(
                        "stock_reconstruido"
                    ),

                "sugerencia":
                    (
                        "No hay movimientos posteriores "
                        "claros para corregir el tramo"
                    ),

                "prioridad":
                    "media"
            })

    return sugerencias


# API SIMPLE
def ejecutar_sugerencias(historial):

    sugerencias = sugerir_correcciones(historial)

    # Separar accionables de revisión manual
    accionables = [s for s in sugerencias if s["tipo"] != "revision_manual"]
    revision    = [s for s in sugerencias if s["tipo"] == "revision_manual"]

    return {
        "total_sugerencias": len(accionables),
        "sugerencias": accionables,
        "revision_manual": revision,          # siguen accesibles si los necesitás
        "total_revision_manual": len(revision)
    }
