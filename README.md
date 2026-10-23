# Cuidado con Rikochet — Retail Data Platform

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pipeline de **Data Engineering** que consume los datos operacionales del simulador [retail-operations-simulator](https://github.com/fabianmm83/retail-operations-simulator) y los transforma en un modelo analítico con KPIs y dashboard visual.

Este repositorio implementa la segunda mitad del ecosistema **Cuidado con Rikochet**:

```text
retail-operations-simulator     →  produce datos operacionales
              ↓
retail-data-platform            →  los ingesta, valida, transforma y analiza
              ↓
React Dashboard                 →  visualización de KPIs
Tabla de contenido
¿Qué es esto?

Arquitectura

Stack técnico

Capas del pipeline

Modelo de datos

Ingesta incremental

API de KPIs

Dashboard React

Instalación y uso

Estructura del proyecto

Próximos pasos

Licencia

¿Qué es esto?
retail-data-platform es el pipeline de datos del ecosistema Cuidado con Rikochet. Transforma los datos del simulador en analítica accionable a través de 5 capas:

RAW — copia fiel de la fuente.

STAGING — datos limpios y tipados.

ANALYTICAL — modelo estrella (dims + facts).

KPIS — métricas precalculadas.

Dashboard — visualización interactiva.

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
│  RAW (copia fiel de la fuente)                             │
│  8 tablas · 11,339 filas                                    │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │  TRANSFORMATION (SQL, idempotente)
                       ▼
┌────────────────────────────────────────────────────────────┐
│  STAGING (limpio, tipado, con CHECK constraints)           │
│  8 tablas · 11,339 filas                                    │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │  TRANSFORMATION (star schema)
                       ▼
┌────────────────────────────────────────────────────────────┐
│  ANALYTICAL (modelo estrella)                              │
│  6 dimensiones + 1 fact · 15,157 filas                      │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │  TRANSFORMATION (agregaciones)
                       ▼
┌────────────────────────────────────────────────────────────┐
│  KPIS (métricas precalculadas)                             │
│  4 tablas · 218 filas                                       │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │  FastAPI (puerto 8001)
                       ▼
┌────────────────────────────────────────────────────────────┐
│  API REST (9 endpoints)                                     │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │  React + Vite (puerto 5173)
                       ▼
┌────────────────────────────────────────────────────────────┐
│  DASHBOARD (5 páginas responsive)                           │
│  Overview · Sales · Products · States · Channels            │
└────────────────────────────────────────────────────────────┘
Stack técnico
Categoría	Tecnología
Lenguaje (backend)	Python 3.13
Conexión a DBs	psycopg 3 + SQLAlchemy 2.1
Migraciones	Alembic 1.20
Almacenamiento	PostgreSQL 16 (en Docker)
API	FastAPI 0.115
Lenguaje (frontend)	TypeScript 5.6
Framework UI	React 19 + Vite 7
Estilos	Tailwind CSS 3
Data fetching	TanStack Query 5
Gráficos	Recharts 2
Routing	React Router 7
Testing	pytest
Linting	Ruff
Capas del pipeline
RAW
Copia fiel de los datos del simulador. Sin transformar.

Metadata de ingesta: _raw_id, _source_id, _ingested_at, _ingestion_run_id, _source_table.

Tablas (8): customers, orders, order_items, states, categories, locations, products, product_variants.

STAGING
Datos limpios y tipados. Enums validados por CHECK constraints. Columnas derivadas (age, line_count).

ANALYTICAL
Modelo estrella con surrogate keys deterministas (ROW_NUMBER()).

Dimensiones (6): dim_date, dim_state, dim_customer, dim_product, dim_variant, dim_warehouse.

Hechos (1): fact_sales (grano: 1 fila = 1 línea de orden).

KPIS
Métricas precalculadas con TRUNCATE + INSERT.

Tablas (4): revenue_daily, revenue_by_product, revenue_by_state, revenue_by_channel.

API
FastAPI en puerto 8001. Sirve los KPIs al dashboard.

Endpoints (9):

GET /health

GET /health/database

GET /api/v1/kpis/overview

GET /api/v1/kpis/revenue/daily

GET /api/v1/kpis/revenue/products

GET /api/v1/kpis/revenue/states

GET /api/v1/kpis/revenue/channels

GET /api/v1/kpis/revenue/categories

GET /api/v1/kpis/revenue/daily/raw

Dashboard
React + Vite en puerto 5173. Diseño responsive (móvil, tablet, desktop).

Páginas (5):

Overview — 8 KPIs + gráficos (pie por canal, bar por categoría).

Sales — serie temporal + comparación por canal.

Products — top 10 + tabla ordenable.

States — distribución geográfica con colores por grupo.

Channels — comparativa ONLINE vs STORE con insight.

Modelo de datos
Schemas
text
retail_analytics
├── raw           ← copia fiel
├── staging       ← limpio y tipado
├── analytical    ← modelo estrella
├── kpis          ← métricas precalculadas
├── dq            ← data quality (pendiente V1.1)
└── meta          ← control del pipeline
Conteos actuales
Schema	Tablas	Filas
raw	8	11,339
staging	8	11,339
analytical	7	15,157
kpis	4	218
meta	2	runs + watermarks
Ingesta incremental
El pipeline usa watermarks para traer solo datos nuevos.

text
1. Leer watermark de la entidad
2. Extraer del origen los registros > watermark
3. Cargar a RAW con UPSERT (idempotente)
4. Actualizar watermark con la fecha/id del último registro
Verificado: correr el pipeline dos veces no duplica datos.

API de KPIs
FastAPI en http://localhost:8001. Documentación automática en /docs.

Ejemplo: Overview
bash
curl http://localhost:8001/api/v1/kpis/overview
json
{
  "total_revenue": "257536.00",
  "total_orders": 406,
  "total_units": 464,
  "aov": "634.33",
  "online_revenue": "157518.00",
  "store_revenue": "100018.00",
  "online_share": "0.6116",
  "top_state": "Estado de México",
  "top_category": "PLAYERAS"
}
Dashboard React
React + Vite en http://localhost:5173. Diseño responsive con Tailwind CSS.

Páginas
Overview
Snapshot general del negocio. 8 KPIs principales + 2 gráficos.

Sales
Análisis de ventas. Serie temporal con área, comparación por canal, detalle en tabla.

Products
Top 10 productos con gráfico de barras horizontal. Tabla completa con 32 productos, ordenable por revenue/units/orders/avg_price.

States
Distribución geográfica. Gráfico horizontal coloreado por grupo de ingreso (ALTO/MEDIO/BAJO) + tabla detallada con share.

Channels
Comparativa ONLINE vs STORE. Pie chart + bar chart + tarjetas detalladas + insight destacando que ONLINE supera a STORE (premisa del negocio).

Instalación y uso
Requisitos
Docker Desktop corriendo

Python 3.13

Node.js 20+ y npm 10+

Git

El simulador (retail-operations-simulator) con datos

Setup backend
bash
# Clonar
git clone https://github.com/fabianmm83/retail-data-platform.git
cd retail-data-platform

# Crear venv
python -m venv .venv
.venv\Scripts\activate

# Instalar
pip install -e ".[dev]"

# Configurar .env
copy .env.example .env

# Levantar PostgreSQL
docker compose up -d

# Aplicar migraciones
alembic upgrade head
Setup dashboard
bash
cd dashboard
npm install
Uso diario
Terminal 1 — Pipeline + API:

bash
cd retail-data-platform
.venv\Scripts\activate

# Pipeline completo (RAW → STAGING → ANALYTICAL → KPIS)
python -m app.pipeline --entities all
python -m app.staging --entities all
python -m app.analytical --entities all
python -m app.kpis --entities all

# API
uvicorn app.main:app --reload --port 8001
Terminal 2 — Dashboard:

bash
cd retail-data-platform/dashboard
npm run dev
Abrir:

API docs: http://localhost:8001/docs

Dashboard: http://localhost:5173

Estructura del proyecto
text
retail-data-platform/
├── alembic/                    # 10 migraciones
├── app/
│   ├── core/                   # config
│   ├── db/                     # engines
│   ├── ingestion/              # extractores + loader
│   ├── raw/                    # 8 modelos RAW
│   ├── staging/                # 8 modelos STAGING
│   ├── analytical/             # 6 dims + 1 fact
│   ├── kpis/                   # 4 KPIs
│   ├── meta/                   # watermarks + runs
│   ├── api/                    # FastAPI
│   ├── schemas/                # Pydantic
│   └── pipeline/               # orquestador
├── dashboard/                  # React app
│   ├── src/
│   │   ├── components/         # Layout, KPICard, Grid, etc.
│   │   ├── pages/              # 5 páginas
│   │   └── lib/                # api, format, hooks
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docs/
│   └── reportes/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── ARCHITECTURE.md
Próximos pasos
V1.1 — Completar entidades
□ Extractor de shipments
□ Extractor de suppliers
□ Extractor de purchase orders
□ Extractor de returns
□ Extractor de inventory_movements
□ fact_inventory
□ fact_shipments
□ fact_purchases
V1.2 — Data Quality
□ Capa VALIDATION con reglas DQ
□ DQ Score
□ Rechazos y reconciliación
V1.3 — Dashboard extendido
□ Páginas: Inventory, Logistics, Procurement, Customers
□ Filtros globales (fecha, estado, canal)
□ Comparación de periodos
V2 — Orquestación
□ Airflow para orquestar el pipeline
□ DAG con dependencias
□ Scheduling automático
V3 — dbt
□ Migrar transformaciones a dbt
□ Tests de dbt
□ Documentación de linaje
V4 — Cloud
□ Migrar a BigQuery o Snowflake
□ Particionamiento y clustering
□ CI/CD con GitHub Actions
Licencia
MIT. Ver LICENSE para detalles.

Repositorios relacionados
retail-operations-simulator — Simulador de operaciones.

retail-data-platform — Este repositorio.

Contacto
GitHub: @fabianmm83

