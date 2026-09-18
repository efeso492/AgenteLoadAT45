INSERT INTO dbo.Auditoria (
    nombre_archivo,
    ruta_archivo,
    tamano_bytes,
    checksum_sha256,
    fecha_modificacion,
    fecha_carga,
    registros_cargados,
    estado,
    observacion
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);