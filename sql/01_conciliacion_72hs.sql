WITH mayor AS (
    SELECT
        ref_comprobante,
        CAST(fecha_contable AS DATE) AS fecha_contable,
        monto AS monto_mayor,
        descripcion AS concepto_mayor
    FROM `YOUR_PROJECT_ID.dataset_audit.libro_mayor`
),
banco AS (
    SELECT
        ref_comprobante AS ref_banco,
        CAST(fecha_banco AS DATE) AS fecha_banco,
        monto AS monto_banco,
        descripcion AS descripcion_banco
    FROM `YOUR_PROJECT_ID.dataset_audit.extracto_bancario`
)
SELECT
    COALESCE(m.ref_comprobante, b.ref_banco) AS ref_comprobante,
    m.fecha_contable,
    b.fecha_banco,
    DATE_DIFF(b.fecha_banco, m.fecha_contable, DAY) AS dias_diferencia_clearing,
    m.monto_mayor,
    b.monto_banco,
    (COALESCE(m.monto_mayor, 0) - (COALESCE(b.monto_banco, 0) * -1)) AS diferencia_monto,

    CASE
        WHEN m.ref_comprobante IS NOT NULL
             AND b.ref_banco IS NOT NULL
             AND m.monto_mayor = (b.monto_banco * -1)
             AND DATE_DIFF(b.fecha_banco, m.fecha_contable, DAY) BETWEEN 0 AND 3
            THEN 'CONCILIADO_DENTRO_DE_CLEARING'

        WHEN m.ref_comprobante IS NOT NULL
             AND b.ref_banco IS NOT NULL
             AND m.monto_mayor = (b.monto_banco * -1)
             AND DATE_DIFF(b.fecha_banco, m.fecha_contable, DAY) < 0
            THEN 'ALERTA_BANCO_ANTERIOR_A_MAYOR'

        WHEN m.ref_comprobante IS NOT NULL
             AND b.ref_banco IS NOT NULL
             AND m.monto_mayor = (b.monto_banco * -1)
             AND DATE_DIFF(b.fecha_banco, m.fecha_contable, DAY) > 3
            THEN 'CONCILIADO_FUERA_DE_TERMINO'

        WHEN m.ref_comprobante IS NOT NULL
             AND b.ref_banco IS NOT NULL
             AND m.monto_mayor <> (b.monto_banco * -1)
            THEN 'DISCREPANCIA_DE_MONTO'

        WHEN m.ref_comprobante IS NOT NULL AND b.ref_banco IS NULL
            THEN 'PENDIENTE_ACREDITACION_BANCO'

        WHEN m.ref_comprobante IS NULL AND b.ref_banco IS NOT NULL
            THEN 'OMISION_REGISTRO_MAYOR'

        ELSE 'REVISION_MANUAL'
    END AS estado_audit_conciliacion

FROM mayor m
FULL OUTER JOIN banco b
    ON m.ref_comprobante = b.ref_banco;