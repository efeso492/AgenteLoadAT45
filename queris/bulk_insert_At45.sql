BULK INSERT At45_Staging
FROM '{ruta_archivo}'
WITH
(
    ROWTERMINATOR = '0x0A'
)