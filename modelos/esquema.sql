-- ============================================================
--  Esquema de la base de datos · GestorTaller
--  Cuatro tablas relacionadas:
--    clientes  ->  vehiculos  ->  incidencias  ->  reparaciones
-- ============================================================

PRAGMA foreign_keys = ON;   -- hace que SQLite respete las claves foráneas

-- Un cliente puede tener varios vehículos.
CREATE TABLE IF NOT EXISTS clientes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre     TEXT NOT NULL,
    cif        TEXT,            -- DNI / NIF / CIF
    telefono   TEXT,
    domicilio  TEXT,
    numero     TEXT,            -- nº de la calle (puede llevar letra: "12B")
    cp         TEXT,
    poblacion  TEXT
);

-- Cada vehículo pertenece a un cliente (cliente_id).
CREATE TABLE IF NOT EXISTS vehiculos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula     TEXT NOT NULL UNIQUE,   -- no se puede repetir: identifica al coche
    marca_modelo  TEXT NOT NULL,
    cliente_id    INTEGER NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- Cada incidencia es una entrada del coche al taller (una orden de trabajo).
CREATE TABLE IF NOT EXISTS incidencias (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo_id    INTEGER NOT NULL,
    fecha_entrada  TEXT NOT NULL,          -- se guarda como AAAA-MM-DD
    fecha_entrega  TEXT,                   -- se guarda como AAAA-MM-DD
    kilometros     INTEGER,
    combustible    TEXT,                   -- 0, 1/4, 1/2, 3/4, 4/4
    estado         TEXT NOT NULL DEFAULT 'recepcionado'
                   CHECK (estado IN ('recepcionado', 'en reparación',
                                     'terminado', 'entregado')),
    recoger_piezas TEXT DEFAULT 'No',      -- ¿el cliente quiere las piezas? Sí/No
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)
);

-- Una incidencia tiene una o varias líneas de reparación.
-- (En el programa original eran 5 líneas fijas; aquí lo hacemos flexible.)
CREATE TABLE IF NOT EXISTS reparaciones (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id  INTEGER NOT NULL,
    descripcion    TEXT NOT NULL,
    FOREIGN KEY (incidencia_id) REFERENCES incidencias(id) ON DELETE CASCADE
);
