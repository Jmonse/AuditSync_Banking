import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_audit_data(n_rows=1000):
    np.random.seed(42)
    start_date = datetime(2026, 3, 1)

    clientes = [f"Cliente_{i}" for i in range(1, 51)]
    proveedores = [f"Proveedor_{i}" for i in range(1, 21)]
    servicios = ['EPEC', 'Aguas Cordobesas', 'Telecom', 'Ecogas', 'Municipalidad']
    entidades_lista = clientes + proveedores + servicios
    entidades_generadas = np.random.choice(entidades_lista, n_rows)

    mapeo_tipo = {c: 'Cobro' for c in clientes}
    mapeo_tipo.update({p: 'Pago' for p in proveedores})
    mapeo_tipo.update({s: 'Pago' for s in servicios})

    # 1. BASE VERDAD TERRENA (Ground Truth)
    data = {
        'id_real': range(1, n_rows + 1),
        'fecha': [start_date + timedelta(days=int(np.random.randint(0, 20))) for _ in range(n_rows)],
        'monto_base': np.round(np.random.uniform(1000, 100000, n_rows), 2),
        'entidad': entidades_generadas,
        'tipo': [mapeo_tipo[entidad] for entidad in entidades_generadas]
    }
    df_truth = pd.DataFrame(data)

    # Convención Libro Mayor: Pagos (-), Cobros (+)
    df_truth['monto_mayor'] = np.where(df_truth['tipo'] == 'Pago', df_truth['monto_base'] * -1, df_truth['monto_base'])
    # Convención Extracto Bancario Crudo (Espejo): Débitos/Pagos (+), Créditos/Cobros (-)
    df_truth['monto_banco'] = df_truth['monto_mayor'] * -1

    # --- LIBRO MAYOR ---
    df_ledger = df_truth.copy()
    df_ledger['ref_comprobante'] = [f"TRX-{1000 + i}" for i in df_ledger['id_real']]
    df_ledger['descripcion'] = df_ledger['tipo'] + " - " + df_ledger['entidad']
    df_ledger['fecha_contable'] = df_ledger['fecha'].dt.strftime('%Y-%m-%d')
    df_ledger['monto'] = df_ledger['monto_mayor']

    # --- EXTRACTO BANCARIO ---
    df_bank = df_truth.copy()
    df_bank['ref_comprobante'] = [f"TRX-{1000 + i}" for i in df_bank['id_real']]
    df_bank['descripcion'] = "BCO_MOV_" + df_bank['entidad'].str[:4].str.upper()
    df_bank['monto'] = df_bank['monto_banco']

    # Asignación de descalces de clearing parametrizados:
    # Registros 0 a 799: Clearing a término (0 a 3 días)
    # Registros 800 a 979: Clearing fuera de término (4 a 7 días)
    clearing_days = np.zeros(n_rows, dtype=int)
    clearing_days[0:800] = np.random.randint(0, 4, size=800)
    clearing_days[800:980] = np.random.randint(4, 8, size=180)

    # Registros 980 a 989: ALERTA - Banco registra ANTES que el Mayor (-1 a -2 días)
    clearing_days[980:990] = np.random.randint(-2, 0, size=10)

    df_bank['fecha_banco'] = (df_bank['fecha'] + pd.to_timedelta(clearing_days, unit='D')).dt.strftime('%Y-%m-%d')

    # INYECCIÓN CONTROLADA DE ANOMALÍAS DE AUDITORÍA:

    # Anomalía A: DISCREPANCIA_DE_MONTO (Índice 0 -> Error de tipeo de $10 en el Mayor)
    df_ledger.loc[0, 'monto'] = np.round(df_ledger.loc[0, 'monto'] + 10.00, 2)

    # Anomalía B: PENDIENTE_ACREDITACION_BANCO (Índices 990 a 999 se omiten en el banco)
    # Simula cheques diferidos en cartera o depósitos no acreditados al cierre
    df_bank = df_bank.iloc[:990].copy()

    # Anomalía C: OMISION_REGISTRO_MAYOR (Débitos bancarios directos no contabilizados)
    # Corrección de Signo: En el extracto crudo, un débito/gasto bancario es POSITIVO (+)
    # para que al normalizar (* -1) quede como EGRESO (-).
    fees = pd.DataFrame([
        {'ref_comprobante': 'TRX-FEE-01', 'fecha_banco': '2026-03-25', 'monto': 1500.00,
         'descripcion': 'COMISION MANTENIMIENTO CTA'},
        {'ref_comprobante': 'TRX-TAX-02', 'fecha_banco': '2026-03-28', 'monto': 450.00,
         'descripcion': 'IMP LEY 25413 DEBITO BCO'},
        {'ref_comprobante': 'TRX-TAX-03', 'fecha_banco': '2026-03-30', 'monto': 315.00,
         'descripcion': 'RETENCION IIBB SIRCREB'}
    ])
    df_bank = pd.concat([df_bank, fees], ignore_index=True)

    # Filtrar columnas finales limpias
    cols_ledger = ['ref_comprobante', 'fecha_contable', 'monto', 'descripcion']
    cols_bank = ['ref_comprobante', 'fecha_banco', 'monto', 'descripcion']

    return df_ledger[cols_ledger], df_bank[cols_bank]


if __name__ == "__main__":
    ledger, bank = generate_audit_data()

    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    ledger.to_csv(os.path.join(output_dir, "libro_mayor.csv"), index=False)
    bank.to_csv(os.path.join(output_dir, "extracto_bancario.csv"), index=False)

    print("✅ Datasets sintéticos generados exitosamente en data/raw/")
    print(f" Total filas en Libro Mayor: {len(ledger)}")
    print(f" Total filas en Extracto Bancario: {len(bank)}")