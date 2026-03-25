import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_audit_data(n_rows=1000):
    np.random.seed(42)
    
    start_date = datetime(2026, 3, 1)
    
    # 1. LA VERDAD ECONÓMICA
    
    # Generación dinámica de entidades
    # Creamos 50 clientes y 20 proveedores automáticamente
    clientes = [f"Cliente_{i}" for i in range(1, 51)] 
    proveedores = [f"Proveedor_{i}" for i in range(1, 21)]
    servicios = ['EPEC', 'Aguas Cordobesas', 'Telecom', 'Ecogas', 'Municipalidad']
    
    entidades_lista = clientes + proveedores + servicios
    entidades_generadas = np.random.choice(entidades_lista, n_rows)
    
    # Armamos el diccionario de mapeo dinámicamente
    mapeo_tipo = {}
    for c in clientes: mapeo_tipo[c] = 'Cobro'
    for p in proveedores: mapeo_tipo[p] = 'Pago'
    for s in servicios: mapeo_tipo[s] = 'Pago'
    
    data = {
        'id_real': range(1, n_rows + 1),
        'fecha': [start_date + timedelta(days=np.random.randint(0, 25)) for _ in range(n_rows)],
        'monto_base': np.round(np.random.uniform(1000, 100000, n_rows), 2),
        'entidad': entidades_generadas,
        'tipo': [mapeo_tipo[entidad] for entidad in entidades_generadas]
    }
    df_truth = pd.DataFrame(data)
    
    # Lógica financiera: Si es Pago, el monto real es salida (-). Si es Cobro, es entrada (+).
    df_truth['monto'] = np.where(df_truth['tipo'] == 'Pago', df_truth['monto_base'] * -1, df_truth['monto_base'])

    # 2. EL LIBRO MAYOR (Lo que anota el administrativo)
    df_ledger = df_truth.copy()
    df_ledger.loc[0, 'monto'] = df_ledger.loc[0, 'monto'] + 10.00 # El famoso "Error de Dedo"
    df_ledger['descripcion'] = df_ledger['tipo'] + " - " + df_ledger['entidad']

    # 3. EL EXTRACTO BANCARIO (Lo que dice el banco)
    df_bank = df_truth.copy()
    # Ventana de Clearing: El banco a veces tarda 1 a 3 días en registrar
    df_bank['fecha'] = df_bank['fecha'] + pd.to_timedelta(np.random.randint(0, 4, n_rows), unit='d')
    df_bank['descripcion'] = "BCO_MOV_" + df_bank['entidad'].str[:4].str.upper() + "_REF" + df_bank['id_real'].astype(str)
    
    # Comisiones ocultas (El banco te saca plata sin avisar)
    fees = pd.DataFrame({
        'id_real': [None], 'fecha': [datetime(2026, 3, 30)], 
        'monto_base': [1500.00], 'tipo': ['Pago'], 'monto': [-1500.00],
        'entidad': ['BANCO'], 'descripcion': ['COMISION MANTENIMIENTO CTA']
    })
    df_bank = pd.concat([df_bank, fees], ignore_index=True)

    # Limpiamos las columnas de trampa
    df_ledger = df_ledger.drop(columns=['id_real', 'entidad', 'monto_base', 'tipo'])
    df_bank = df_bank.drop(columns=['id_real', 'entidad', 'monto_base', 'tipo'])

    return df_ledger, df_bank

if __name__ == "__main__":
    ledger, bank = generate_audit_data()
    ledger.to_csv("data/raw/libro_mayor.csv", index=False)
    bank.to_csv("data/raw/extracto_bancario.csv", index=False)
    print("¡Nuevos archivos generados con Ingresos y Egresos reales!")