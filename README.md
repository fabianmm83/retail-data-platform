# Cuidado con Rikochet — Retail Data Platform

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-red.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.20-orange.svg)](https://alembic.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pipeline de **Data Engineering** que consume los datos operacionales del simulador [retail-operations-simulator](https://github.com/fabianmm83/retail-operations-simulator) y los transforma en un modelo analítico listo para KPIs y dashboard.

Este repositorio implementa la segunda mitad del ecosistema **Cuidado con Rikochet**:

```text
retail-operations-simulator     →  produce datos operacionales
              ↓
retail-data-platform            →  los ingesta, valida, transforma y analiza
Tabla de contenido
¿Qué es esto?

Arquitectura

Stack técnico

Capas del pipeline

Modelo de datos

Ingesta incremental

Instalación y uso

Estructura del proyecto

Próximos pasos

Licencia

¿Qué es esto?
retail-data-platform es el pipeline de datos del ecosistema Cuidado con Rikochet. Su responsabilidad es:

Extraer los datos del simulador (retail-operations-simulator).

Cargar los datos crudos a una capa RAW (copia fiel, sin transformar).

Validar que los datos cumplan reglas de calidad.

Limpiar y tipar los datos en STAGING.

Modelar los datos en un esquema estrella (ANALYTICAL).

Calcular KPIs precalculados.

Servir los KPIs vía API para el dashboard React.

La filosofía sigue el método Google de data engineering:

text
1. Ingest everything raw
2. Store it in a canonical form
3. Validate early
4. Model for analysis
5. Serve fast
Arquitectura
text
┌────────────────────────────────────────────────────────────┐
│  retail-operations-simulator (fuente)                      │
│  PostgreSQL en localhost:5434                              │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │  INGESTION (incremental por watermark)
                       ▼
┌────────────────────────────────────────────────────────────┐
│  INGESTION                                                  │
│  - WatermarkStore (control de ingesta por entidad)         │
│  - Extractores (customers, orders, order_items, ...)       │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│  RAW (copia fiel de la fuente)                             │
│  - Sin transformar                                          │
│  - Metadata de ingesta (_ingested_at, _ingestion_run_id)   │
│  - Idempotencia por _source_id                              │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│  VALIDATION (reglas de Data Quality)                       │
│  - PASS / WARN / FAIL                                       │
│  - Rechazos a dq.rejected_records                           │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│  STAGING (limpio, tipado, deduplicado)                     │
│  - Tipos correctos                                          │
│  - Sin duplicados                                           │
│  - Derivaciones básicas                                     │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│  ANALYTICAL (modelo estrella)                              │
│  - Dimensiones: dim_date, dim_customer, dim_product, ...   │
│  - Hechos: fact_sales, fact_inventory, fact_shipments, ... │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│  KPIs (métricas precalculadas)                             │
│  - Revenue, Orders, AOV, Inventory Health, Logistics       │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│  DASHBOARD (React + FastAPI)                               │
└────────────────────────────────────────────────────────────┘
Stack técnico
Categoría	Tecnología
Lenguaje	Python 3.13
Conexión a DBs	psycopg 3 + SQLAlchemy 2.1
Migraciones	Alembic 1.20
Almacenamiento	PostgreSQL 16 (en Docker)
Orquestación	Python CLI (V1) · Airflow (V2)
Transformaciones	SQL puro + SQLAlchemy (V1) · dbt (V3)
API de KPIs	FastAPI
Dashboard	React + TypeScript + Vite (planeado)
Testing	pytest
Linting	Ruff
Capas del pipeline
1. INGESTION
Extrae los datos del simulador de forma incremental usando watermarks. Cada entidad tiene su propio watermark que dice hasta dónde se ha ingestado.

Componentes:

WatermarkStore: lee/escribe watermarks en meta.watermarks.

RawLoader: UPSERT idempotente por _source_id.

extractors/*: un extractor por entidad.

Modos:

full load: trae todos los datos cada vez (customers).

incremental: solo trae lo nuevo desde el último watermark (orders, order_items).

2. RAW
Copia fiel de los datos del simulador. Sin transformar, sin limpiar.

Reglas:

Mismos nombres de columna que la fuente.

Enums guardados como String (para tolerancia).

Metadata de ingesta: _raw_id, _source_id, _ingested_at, _ingestion_run_id, _source_table.

Idempotencia garantizada por UNIQUE en _source_id.

Por qué existe: si algo sale mal en capas siguientes, se puede reprocesar desde RAW. Es la fuente de verdad histórica.

3. VALIDATION (pendiente)
Reglas de Data Quality sobre los datos RAW antes de pasarlos a STAGING.

Tipos de validación:

Estructura, nulidad, unicidad, rangos.

Referencial (FKs existen).

Lógica (total = subtotal + shipping - discount).

Temporal (shipped_at >= order_date).

Resultado: PASS / WARN / FAIL. Los rechazos van a dq.rejected_records.

4. STAGING (pendiente)
Datos limpios, tipados y deduplicados.

Transformaciones:

Conversión de tipos (texto → número, fecha, decimal).

Normalización (mayúsculas, trim).

Deduplicación.

Derivaciones básicas.

5. ANALYTICAL (pendiente)
Modelo dimensional tipo estrella.

Dimensiones:

dim_date, dim_customer, dim_product, dim_variant.

dim_warehouse, dim_state.

Hechos:

fact_sales, fact_inventory, fact_shipments, fact_purchases.

6. KPIs (pendiente)
Métricas precalculadas para servir rápido al dashboard.

Familias:

Ventas: Revenue, Orders, Units Sold, AOV.

Inventario: Stock, Low Stock, Stockout, Turnover.

Logística: On-Time Delivery, Avg Delivery Time, Carrier Performance.

Procurement: Supplier Lead Time, Reliability, Cost.

7. DASHBOARD (pendiente)
Aplicación React que consume los KPIs vía API intermedia.

Modelo de datos
Schemas
text
retail_analytics
├── raw           ← copia fiel de la fuente
├── staging       ← limpio y tipado
├── analytical    ← modelo estrella (dims + facts)
├── kpis          ← métricas precalculadas
├── dq            ← data quality
└── meta          ← control del pipeline
Tablas RAW implementadas (11)
Tabla RAW	Estado	Modo
raw.customers	✅ poblada (10,000)	full
raw.orders	✅ poblada (188)	incremental
raw.order_items	✅ poblada (435)	incremental
raw.products	pendiente	—
raw.product_variants	pendiente	—
raw.states	pendiente	—
raw.locations	pendiente	—
raw.shipments	pendiente	—
raw.carriers	pendiente	—
raw.categories	pendiente	—
raw.inventory_movements	pendiente	—
Tablas meta
meta.watermarks: control de ingesta por entidad.

meta.pipeline_runs: log de cada corrida del pipeline.

Ingesta incremental
El pipeline usa watermarks para saber hasta dónde llegó la última ingesta.

Cómo funciona
text
1. Leer watermark de la entidad
       ↓
2. Extraer del origen los registros > watermark
       ↓
3. Cargar a RAW con UPSERT (idempotente)
       ↓
4. Actualizar watermark con la fecha/id del último registro
Ejemplo con orders
text
Watermark actual: last_date=2026-05-15, last_id=ORD-2026-003421

Query al origen:
    SELECT * FROM orders
    WHERE order_date > '2026-05-15'
       OR (order_date = '2026-05-15' AND order_number > 'ORD-2026-003421')
    ORDER BY order_date, order_number

Resultado: solo las órdenes nuevas.

Después de cargar:
    watermark.last_date = 2026-05-20
    watermark.last_id   = ORD-2026-004012
    watermark.rows_last_run = 47
    watermark.status    = SUCCESS
Idempotencia
Si corres el pipeline dos veces seguidas sin cambios en el origen:

text
Segunda corrida:
  extraídas 0 filas
  0 filas procesadas

Conteos en RAW: sin cambios (ni duplicados).
Verificado y funcionando.

Instalación y uso
Requisitos
Docker Desktop corriendo

Python 3.13

Git

El simulador (retail-operations-simulator) corriendo con datos

Setup
bash
# Clonar
git clone https://github.com/fabianmm83/retail-data-platform.git
cd retail-data-platform

# Crear venv
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -e ".[dev]"

# Configurar .env
copy .env.example .env

# Levantar PostgreSQL del data platform
docker compose up -d

# Aplicar migraciones
alembic upgrade head
Uso
bash
# Correr todo el pipeline (customers, orders, order_items)
python -m app.pipeline --entities all

# Correr una entidad específica
python -m app.pipeline --entities orders

# Correr varias entidades
python -m app.pipeline --entities orders,order_items

# Verbose
python -m app.pipeline --entities all --verbose
Verificar el estado
bash
# Conteos en RAW
docker exec retail-analytics-postgres psql -U analytics_user -d retail_analytics -c "SELECT COUNT(*) FROM raw.orders;"

# Watermarks
docker exec retail-analytics-postgres psql -U analytics_user -d retail_analytics -c "SELECT * FROM meta.watermarks;"

# Runs del pipeline
docker exec retail-analytics-postgres psql -U analytics_user -d retail_analytics -c "SELECT * FROM meta.pipeline_runs ORDER BY id;"
Estructura del proyecto
text
retail-data-platform/
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 3d3d7d8a42b5_001_create_schemas.py
│       ├── 7eb1b5be4e23_002_create_raw_orders.py
│       ├── aab900c3942f_003_create_raw_core_tables.py
│       └── 66baa12b65f1_004_create_meta_tables.py
├── alembic.ini
├── app/
│   ├── core/                    # config
│   ├── db/                      # engines + Base
│   ├── ingestion/
│   │   ├── extractors/
│   │   │   ├── customers.py
│   │   │   ├── orders.py
│   │   │   └── order_items.py
│   │   ├── loader.py            # UPSERT a RAW
│   │   ├── source_models.py     # modelos del origen
│   │   └── watermark_store.py
│   ├── raw/                     # 11 modelos RAW
│   ├── meta/                    # watermarks + pipeline_runs
│   ├── staging/                 # (pendiente)
│   ├── analytical/              # (pendiente)
│   ├── kpis/                    # (pendiente)
│   ├── validation/              # (pendiente)
│   ├── api/                     # (pendiente)
│   └── pipeline/
│       ├── runner.py            # orquestador
│       └── __main__.py          # CLI
├── dashboard/                   # (planeado)
├── tests/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── ARCHITECTURE.md
Próximos pasos
□ BLOQUE 5 — STAGING: limpieza, tipado, deduplicación.
□ BLOQUE 6 — ANALYTICAL: dims + facts (modelo estrella).
□ BLOQUE 7 — KPIs: precalcular métricas de negocio.
□ BLOQUE 8 — API intermedia: FastAPI para servir KPIs.
□ BLOQUE 9 — Dashboard React.
□ Data Quality: reglas + DQ Score + rechazos.
□ Airflow para orquestación (V2).
□ dbt para transformaciones versionadas (V3).
□ Cloud (BigQuery / Snowflake) (V4).
Licencia
MIT. Ver LICENSE para detalles.

Repositorios relacionados
retail-operations-simulator — Simulador de operaciones.

retail-data-platform — Este repositorio.

Contacto
GitHub: @fabianmm83