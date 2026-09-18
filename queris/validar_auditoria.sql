SELECT TOP (1) 1
FROM dbo.Auditoria
WHERE checksum_sha256 = ?
   OR nombre_archivo = ?;