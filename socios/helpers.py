import calendar

def obtener_nombre_del_mes(numero_mes):
    try:
        meses = {
        1: "enero",
        2: "febrero",
        3: "marzo",
        4: "abril",
        5: "mayo",
        6: "junio",
        7: "julio",
        8: "agosto",
        9: "septiembre",
        10: "octubre",
        11: "noviembre",
        12: "diciembre"
    }
        return meses[numero_mes]
    except IndexError:
        return "Mes no válido"
    