# 🏦 AuditSync Banking — Motor de Conciliación Bancaria & Control de Riesgo Financiero

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Google BigQuery](https://img.shields.io/badge/Google%20BigQuery-Sandbox-blue?logo=googlecloud)
![SQL](https://img.shields.io/badge/SQL-Standard%20SQL-orange?logo=postgresql)
![Power BI](https://img.shields.io/badge/Power%20BI-Desktop-yellow?logo=powerbi)
![Status](https://img.shields.io/badge/Estado-Producción-success)

**Autor:** Jonathan Nazareno Monserrat | Estudiante de Contador Público (UNC) & Data Analyst  
**Stack:** SQL (BigQuery) · Python 3.13 · DataGrip · Power BI · pandas · PyCharm Pro  
**Alcance:** Cruce masivo Libro Mayor vs. Extracto Bancario · Tolerancia de Clearing (72 hs) · Matriz de Estados de Auditoría

---

## 📌 Descripción & Contexto de Negocio

**AuditSync Banking** es un motor de conciliación bancaria end-to-end diseñado para automatizar el cruce de partidas financieras entre el Libro Mayor contable y los Extractos Bancarios, reduciendo el trabajo manual de cierre, garantizando la trazabilidad documental e identificando el **Monto en Riesgo** por descalces temporales.

En procesos manuales de conciliación suelen aparecer tres vulnerabilidades críticas:
1. **Ineficiencia Operativa:** Análisis manual fila a fila con alto consumo de horas en cierres mensuales.
2. **Falsos Positivos por Clearing:** Cheques o transferencias con acreditación diferida (24 a 72 hs hábiles) clasificados erróneamente como faltantes.
3. **Falta de Control Interno:** Ocurrencia de débitos no registrados (gastos bancarios, comisiones, impuestos) que distorsionan el saldo real de disponibilidad.

---

## 🏗️ Arquitectura del Data Pipeline

```text
[Data Sources / CSV] ──> [Python Ingestion Script] ──> [Google BigQuery Sandbox] ──> [SQL Engine & CTEs] ──> [Power BI / Processed Evidence]

```

El pipeline cubre el ciclo completo de procesamiento de datos contables:

1. **Ingesta y Evidencia Sintética (`src/generator.py`):** Generación de datasets contables y bancarios parametrizados con volumen realista, patrones de clearing y desvíos operativos controlados. La ejecución del script asegura automáticamente la creación de los directorios requeridos (`data/raw/`).
2. **Data Warehouse & Motor SQL (`sql/01_conciliacion_72hs.sql`):** Procesamiento de datos en **Google BigQuery Sandbox** mediante consultas SQL con CTEs, `FULL OUTER JOIN`, conversión de tipos (`CAST`) y funciones de ventana temporal (`DATE_DIFF`) para catalogar 6 estados de auditoría.
3. **Visualización & FP&A (`notebooks/` & `Power BI`):** Consumo de la vista parametrizada para el seguimiento de KPIs ejecutivos, antigüedad de saldos pendientes y desglose del Monto en Riesgo.

---

## 📊 Matriz de Clasificación & Reglas de Auditoría

El motor SQL evalúa las discrepancias de importes y las ventanas temporales de acreditación mediante las siguientes reglas de negocio:

| Estado de Conciliación | Criterio Técnico / Lógica Contable | Acción de Control |
| --- | --- | --- |
| `CONCILIADO_DENTRO_DE_CLEARING` | Monto coincidente y acreditación bancaria entre 0 y 3 días (`DATE_DIFF`). | Aprobación automática. |
| `CONCILIADO_FUERA_DE_TERMINO` | Monto coincidente pero acreditación bancaria excede las 72 hs (`DATE_DIFF` > 3). | Alerta por ineficiencia en canal de cobro/pago. |
| `ALERTA_BANCO_ANTERIOR_A_MAYOR` | Impacto bancario previo a la registración en el Libro Mayor (`DATE_DIFF` < 0). | Auditoría de corte de documentación contable. |
| `DISCREPANCIA_DE_MONTO` | Comprobante idéntico con diferencia numérica entre sistemas. | Ajuste por error de registración o tipeo. |
| `PENDIENTE_ACREDITACION_BANCO` | Registrado en Libro Mayor sin movimiento correlativo en el banco. | Control de cartera de cheques diferidos / depósitos. |
| `OMISION_REGISTRO_MAYOR` | Movimiento bancario no registrado en la contabilidad de la empresa. | Asiento de ajuste por gastos o retenciones. |

---

## 📈 Resultados & Indicadores de Gestión

| Indicador | Valor / Métrica | Impacto en Negocio |
| --- | --- | --- |
| **Efectividad del Motor** | `99.88%` | Reducción drástica del trabajo manual en el cierre mensual. |
| **Partidas para Revisión Manual** | `0.12%` | Focalización del análisis humano exclusivamente en excepciones complejas. |
| **Monto Auditado** | `$49,724,795.06` | Cobertura integral de la muestra transaccional procesada. |

---

## 🗂️ Estructura del Repositorio

```text
AuditSync_Banking/
├── data/
│   ├── raw/                          # Datasets de entrada (extracto_bancario.csv, libro_mayor.csv)
│   └── processed/                    # Salidas auditables (conciliados_final.csv, Partidas_Pendientes_Marzo.xlsx)
├── docs/
│   └── img/                          # Capturas del Dashboard y gráficos de eficacia
├── sql/
│   └── 01_conciliacion_72hs.sql      # Consulta nativa SQL (BigQuery Standard SQL)
├── notebooks/
│   ├── 01_Exploracion_y_Limpieza.ipynb
│   ├── 02_Motor_de_Conciliacion.ipynb
│   └── 03_Dashboard_Conciliation.ipynb
├── src/
│   └── generator.py                  # Script Python de ingesta y simulación
├── .gitignore                        # Exclusión de entorno virtual y archivos IDE
├── requirements.txt
└── README.md

```

---

## 🛠️ Stack Tecnológico

* **Motor de Datos & SQL:** Google BigQuery Sandbox, Standard SQL.
* **Lenguaje & Entorno:** Python 3.13, PyCharm Pro, DataGrip.
* **Librerías Python:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `openpyxl`.
* **Business Intelligence:** Power BI Desktop (Modelado de datos, DAX).

---

## 🚀 Ejecución Paso a Paso

1. **Clonar el repositorio y configurar el entorno:**

```bash
git clone [https://github.com/Jmonse/AuditSync_Banking.git](https://github.com/Jmonse/AuditSync_Banking.git)
cd AuditSync_Banking
python -m venv .venv
source .venv/Scripts/activate  # Git Bash en Windows
pip install -r requirements.txt

```

2. **Generar los datos sintéticos:**

```bash
python src/generator.py

```

3. **Ejecutar los cuadernos de análisis y motor de conciliación:**
Ejecutar secuencialmente los cuadernos en la carpeta `notebooks/`.
4. **Ejecutar la consulta en BigQuery / DataGrip:**
Cargar las tablas de `data/raw/` en BigQuery Sandbox y desplegar la consulta alojada en `sql/01_conciliacion_72hs.sql`.

---

## 📬 Contacto & Perfil Profesional

**Jonathan Nazareno Monserrat**

Estudiante de Contador Público (UNC) & Data Analyst enfocado en BI, FP&A, Control de Gestión y Auditoría.

* **LinkedIn:** [linkedin.com/in/jonathan-monserrat](https://www.linkedin.com/in/jonathan-monserrat/)
* **GitHub:** [github.com/Jmonse](https://github.com/Jmonse)

```

---

### 2. Comandos para Ejecutar el Commit y Push Finales

Una vez guardados los archivos en PyCharm, abrí la terminal integrando Git Bash y ejecutá:

```bash
git add .
git commit -m "refactor: finaliza pipeline integral, documentacion README y configuracion de gitignore"
git push origin main

```