"""
Datos de ejemplo para la demo.

Rellena la base de datos con tres clientes, sus coches y varias incidencias,
para poder enseñar el autorrelleno, el historial, los estados y los gráficos
sin tener que teclear todo a mano.

Los datos son INVENTADOS y genéricos (proyecto académico): nombres de ejemplo,
DNIs de prueba con letra de control válida y poblaciones cualesquiera.

Solo siembra si la base está vacía, así no se duplican los datos al ejecutarlo
dos veces.

    python datos_ejemplo.py
"""

from modelos.conexion import inicializar_bd, obtener_conexion
from modelos import cliente, vehiculo, incidencia, reparacion


# Cada entrada: datos del cliente, su coche y una lista de incidencias.
EJEMPLOS = [
    {
        "cliente": {
            "nombre": "Ana López García", "cif": "12345678Z",
            "telefono": "600000001", "domicilio": "Calle de Ejemplo", "numero": "1",
            "cp": "28001", "poblacion": "Madrid",
        },
        "vehiculo": {"matricula": "1234BCD", "marca_modelo": "SEAT León 1.6 TDI"},
        "incidencias": [
            {
                "fecha_entrada": "2025-01-15", "fecha_entrega": "2025-01-17",
                "kilometros": 142300, "combustible": "1/2",
                "estado": "entregado", "recoger_piezas": "No",
                "reparaciones": [
                    "Sustitución de pastillas y discos de freno delanteros",
                    "Cambio de aceite y filtro",
                ],
            },
            {
                "fecha_entrada": "2025-05-08", "fecha_entrega": None,
                "kilometros": 151020, "combustible": "1/4",
                "estado": "en reparación", "recoger_piezas": "Sí",
                "reparaciones": ["Revisión de la distribución y bomba de agua"],
            },
        ],
    },
    {
        "cliente": {
            "nombre": "Carlos Martín Ruiz", "cif": "87654321X",
            "telefono": "600000002", "domicilio": "Avenida de Muestra", "numero": "20",
            "cp": "41001", "poblacion": "Sevilla",
        },
        "vehiculo": {"matricula": "5678FGH", "marca_modelo": "Renault Clio 1.2"},
        "incidencias": [
            {
                "fecha_entrada": "2025-03-02", "fecha_entrega": "2025-03-04",
                "kilometros": 89500, "combustible": "3/4",
                "estado": "terminado", "recoger_piezas": "No",
                "reparaciones": [
                    "Diagnosis de avería eléctrica (no arranca)",
                    "Sustitución del motor de arranque",
                    "Carga y prueba de batería",
                ],
            },
        ],
    },
    {
        "cliente": {
            "nombre": "Lucía Fernández Gil", "cif": "11223344B",
            "telefono": "600000003", "domicilio": "Calle de Prueba", "numero": "8",
            "cp": "46001", "poblacion": "Valencia",
        },
        "vehiculo": {"matricula": "9012JKL", "marca_modelo": "Ford Focus 1.5 TDCi"},
        "incidencias": [
            {
                "fecha_entrada": "2025-05-12", "fecha_entrega": None,
                "kilometros": 64200, "combustible": "4/4",
                "estado": "recibido", "recoger_piezas": "No",
                "reparaciones": [
                    "Ruido en tren delantero, revisar rótulas y silentblocks",
                ],
            },
        ],
    },
]


def sembrar():
    inicializar_bd()
    con = obtener_conexion()

    # Si ya hay clientes, no volvemos a sembrar.
    ya_hay = con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    if ya_hay:
        print(f"La base ya tiene {ya_hay} cliente(s); no se insertan datos.")
        con.close()
        return

    try:
        for fila in EJEMPLOS:
            # Cliente -> su id -> vehículo -> sus incidencias -> reparaciones.
            cliente_id = cliente.crear(con, fila["cliente"])
            vehiculo_id = vehiculo.crear(
                con,
                fila["vehiculo"]["matricula"],
                fila["vehiculo"]["marca_modelo"],
                cliente_id,
            )
            for inc in fila["incidencias"]:
                inc_id = incidencia.crear(con, {
                    "vehiculo_id": vehiculo_id,
                    "fecha_entrada": inc["fecha_entrada"],
                    "fecha_entrega": inc["fecha_entrega"],
                    "kilometros": inc["kilometros"],
                    "combustible": inc["combustible"],
                    "estado": inc["estado"],
                    "recoger_piezas": inc["recoger_piezas"],
                })
                reparacion.crear_varias(con, inc_id, inc["reparaciones"])

        # Un único commit al final: o se guarda todo o no se guarda nada.
        con.commit()
        print("Datos de ejemplo insertados correctamente.")
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    sembrar()
