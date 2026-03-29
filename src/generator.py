import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_audit_data(n_rows=1000):
    np.random.seed(42) #Fijamos la semilla para que los resultados sean auditables y reproducibles
    
    start_date = datetime(2026, 3, 1)
    
    # --- FASE 1: LA REALIDAD ECONÓMICA ---
    # Simulamos un entorno de transacciones reales con clientes, proveedores y servicios públicos
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
    
    # Lógica financiera: asignamos el signo según la dirección del flujo de fondos
    df_truth['monto'] = np.where(df_truth['tipo'] == 'Pago', df_truth['monto_base'] * -1, df_truth['monto_base'])

    # --- FASE 2: EL LIBRO MAYOR (Control Interno Vulnerable) ---
    # Simulamos el registro administrativo de la empresa, incluyendo errores humanos y omisiones comunes
    df_ledger = df_truth.copy()
    # "Error de Dedo": Alteramos un monto para testear la detección del motor de auditoría
    df_ledger.loc[0, 'monto'] = df_ledger.loc[0, 'monto'] + 10.00 # El famoso "Error de Dedo"
    df_ledger['descripcion'] = df_ledger['tipo'] + " - " + df_ledger['entidad']

    # --- FASE 3: EL EXTRACTO BANCARIO (Lo que dice el Banco) ---
    # Emulamos el extracto bancario, incorporando el factor de descalce temporal (Clearing)
    df_bank = df_truth.copy()

    # PRINCIPIO DEL ESPEJO CONTABLE:
    # El banco refleja el mismo monto pero con signo opuesto, 
    # ya que para la empresa es un ingreso o egreso, para el banco es lo contrario
    df_bank['monto'] = df_bank['monto'] * -1 
    
    # El banco registra con un retraso de 0 a 3 días, desafiando la conciliación lineal
    df_bank['fecha'] = df_bank['fecha'] + pd.to_timedelta(np.random.randint(0, 4, n_rows), unit='d')
    df_bank['descripcion'] = "BCO_MOV_" + df_bank['entidad'].str[:4].str.upper() + "_REF" + df_bank['id_real'].astype(str)
    
    # Partidas NO Registradas: Inyectamos comisiones bancarias que no figuran en el Libro Mayor
    fees = pd.DataFrame({
        'id_real': [None], 'fecha': [datetime(2026, 3, 30)], 
        'monto_base': [1500.00], 'tipo': ['Pago'], 'monto': [-1500.00],
        'entidad': ['BANCO'], 'descripcion': ['COMISION MANTENIMIENTO CTA']
    })
    df_bank = pd.concat([df_bank, fees], ignore_index=True)

    # Limpieza de metadatos para simular archivos crudos de sistemas contables distintos
    df_ledger = df_ledger.drop(columns=['id_real', 'entidad', 'monto_base', 'tipo'])
    df_bank = df_bank.drop(columns=['id_real', 'entidad', 'monto_base', 'tipo'])

    return df_ledger, df_bank

if __name__ == "__main__":
    ledger, bank = generate_audit_data()
    ledger.to_csv("data/raw/libro_mayor.csv", index=False)
    bank.to_csv("data/raw/extracto_bancario.csv", index=False)
    print("¡Nuevos archivos generados con Ingresos y Egresos reales!")