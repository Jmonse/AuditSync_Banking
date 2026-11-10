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

    data = {
        'id_real': range(1, n_rows + 1),
        'fecha': [start_date + timedelta(days=int(np.random.randint(0, 25))) for _ in range(n_rows)],
        'monto_base': np.round(np.random.uniform(1000, 100000, n_rows), 2),
        'entidad': entidades_generadas,
        'tipo': [mapeo_tipo[entidad] for entidad in entidades_generadas]
    }
    df_truth = pd.DataFrame(data)
    df_truth['monto'] = np.where(df_truth['tipo'] == 'Pago', df_truth['monto_base'] * -1, df_truth['monto_base'])

    # --- LIBRO MAYOR ---
    df_ledger = df_truth.copy()
    df_ledger['ref_comprobante'] = [f"TRX-{1000 + i}" for i in df_ledger['id_real']]
    # Inyección de error operativo ("Error de dedo")
    df_ledger.loc[0, 'monto'] = df_ledger.loc[0, 'monto'] + 10.00
    df_ledger['descripcion'] = df_ledger['tipo'] + " - " + df_ledger['entidad']
    df_ledger['fecha_contable'] = df_ledger['fecha'].dt.strftime('%Y-%m-%d')

    # --- EXTRACTO BANCARIO ---
    df_bank = df_truth.copy()
    df_bank['ref_comprobante'] = [f"TRX-{1000 + i}" for i in df_bank['id_real']]
    df_bank['monto'] = df_bank['monto'] * -1  # Espejo bancario

    # Descalce temporal de clearing (0 a 4 días) - Corrección de unidad 'D'
    df_bank['fecha_banco'] = (
                df_bank['fecha'] + pd.to_timedelta(np.random.randint(0, 5, n_rows), unit='D')).dt.strftime('%Y-%m-%d')
    df_bank['descripcion'] = "BCO_MOV_" + df_bank['entidad'].str[:4].str.upper()

    # Inyección de Gasto Bancario Omitido en Mayor
    fees = pd.DataFrame({
        'id_real': [9999], 'fecha_banco': ['2026-03-30'],
        'monto': [-1500.00], 'ref_comprobante': ['TRX-FEE-99'],
        'descripcion': ['COMISION MANTENIMIENTO CTA']
    })
    df_bank = pd.concat([df_bank, fees], ignore_index=True)

    # Filtrar columnas finales limpias
    cols_ledger = ['ref_comprobante', 'fecha_contable', 'monto', 'descripcion']
    cols_bank = ['ref_comprobante', 'fecha_banco', 'monto', 'descripcion']

    return df_ledger[cols_ledger], df_bank[cols_bank]


if __name__ == "__main__":
    ledger, bank = generate_audit_data()

    # Asegurar creación del directorio data/raw antes de exportar
    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    ledger.to_csv(os.path.join(output_dir, "libro_mayor.csv"), index=False)
    bank.to_csv(os.path.join(output_dir, "extracto_bancario.csv"), index=False)

    print("Archivos CSV sintéticos generados exitosamente en data/raw/")