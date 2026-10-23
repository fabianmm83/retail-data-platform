# Arquitectura — Retail Data Platform

Documento técnico sobre las decisiones de diseño del pipeline de datos y el dashboard.

---

## Tabla de contenido

1. [Visión general](#visión-general)
2. [Filosofía de diseño](#filosofía-de-diseño)
3. [Capas del pipeline](#capas-del-pipeline)
4. [Estructura de schemas](#estructura-de-schemas)
5. [Ingesta incremental](#ingesta-incremental)
6. [Modelo estrella](#modelo-estrella)
7. [KPIs](#kpis)
8. [API](#api)
9. [Dashboard](#dashboard)
10. [Decisiones técnicas](#decisiones-técnicas)
11. [Limitaciones de V1](#limitaciones-de-v1)
12. [Roadmap](#roadmap)

---

## Visión general

El data platform consume datos del simulador y los transforma en analítica visual, siguiendo el **método Google** de data engineering.

```text
1. Ingest everything raw       → capa RAW
2. Store in a canonical form   → capa STAGING
3. Validate early              → capa VALIDATION (V1.2)
4. Model for analysis          → capa ANALYTICAL
5. Serve fast                  → KPIS + API + Dashboard
Todas las operaciones son idempotentes, incrementales, trazables y recuperables.

Filosofía de diseño
Principio 1 — RAW como fuente de verdad
La capa RAW es copia fiel. Nunca se modifica manualmente.

Principio 2 — Idempotencia por diseño
Todo loader usa UPSERT por _source_id. Todo transformer usa TRUNCATE + INSERT. Correr dos veces deja el mismo estado.

Principio 3 — Ingesta incremental
Watermarks por entidad. Solo se trae lo nuevo.

Principio 4 — Surrogate keys deterministas
ROW_NUMBER() ordenado por business key (customer_code, style_code, sku, etc.). Mismo input → mismo key.

Principio 5 — Modelo estrella (Kimball)
Dimensiones desnormalizadas, hechos con FKs a dims, surrogate keys en todo.

Principio 6 — KPIs precalculados
TRUNCATE + INSERT de agregaciones. Los dashboards leen rápido sin recalcular.

Principio 7 — API como contrato
El dashboard consume la API, nunca la DB directamente. Permite cambiar el backend sin tocar el frontend.

Principio 8 — Responsive desde el inicio
El dashboard se diseña para móvil, tablet y desktop. No es un "agregado".

Capas del pipeline
Capa	Estado	Filas	Propósito
INGESTION	✅	—	Extrae del simulador
RAW	✅	11,339	Copia fiel
VALIDATION	⏳ V1.2	—	Reglas de calidad
STAGING	✅	11,339	Limpio y tipado
ANALYTICAL	✅	15,157	Modelo estrella
KPIS	✅	218	Métricas precalculadas
API	✅	—	FastAPI en 8001
DASHBOARD	✅	—	React en 5173
Estructura de schemas
text
retail_analytics
├── raw           ← copia fiel
├── staging       ← limpio y tipado
├── analytical    ← modelo estrella
├── kpis          ← métricas precalculadas
├── dq            ← data quality (pendiente V1.2)
└── meta          ← control del pipeline
Ingesta incremental
Watermark
text
meta.watermarks
├── entity_name
├── last_watermark_date
├── last_watermark_id
├── last_run_at
├── rows_last_run
└── status (SUCCESS | FAILED | RUNNING)
Modos
Full load: customers, states, categories, locations, products, product_variants.

Incremental: orders, order_items (por order_date).

Idempotencia
UPSERT por _source_id con ON CONFLICT DO UPDATE. Verificado: segunda corrida trae 0 filas.

Modelo estrella
Dimensiones (6)
Dim	Surrogate key	Business key
dim_date	date_key (YYYYMMDD)	full_date
dim_state	state_key (INT)	state_id (UUID)
dim_customer	customer_key (INT)	customer_id (UUID)
dim_product	product_key (INT)	product_id (UUID)
dim_variant	variant_key (INT)	variant_id (UUID)
dim_warehouse	warehouse_key (INT)	location_id (UUID)
Hechos (1)
fact_sales: 1 fila = 1 línea de orden. FKs a las 6 dimensiones + business keys (order_id, order_number).

Decisiones clave
Surrogate keys INTEGER (no UUID): más rápidos para JOINs.

Determinismo: ROW_NUMBER() ordenado por business key.

SCD Tipo 2: no en V1 (se puede agregar después sin romper nada).

dim_date generada 2020–2030 con generate_series.

KPIs
Tablas (4)
KPI	Grano	Filas
revenue_daily	día × estado × canal × categoría	174
revenue_by_product	producto × mes	32
revenue_by_state	estado × mes	10
revenue_by_channel	canal × mes	2
Estrategia
TRUNCATE + INSERT full refresh. Con volúmenes actuales (218 filas) es instantáneo. En V2 se puede migrar a incremental.

API
Stack
FastAPI 0.115 + Pydantic 2 + Uvicorn.

Endpoints
Método	Ruta	Descripción
GET	/health	Health check
GET	/health/database	Health DB
GET	/api/v1/kpis/overview	Snapshot general
GET	/api/v1/kpis/revenue/daily	Serie temporal
GET	/api/v1/kpis/revenue/products	Top productos
GET	/api/v1/kpis/revenue/states	Revenue por estado
GET	/api/v1/kpis/revenue/channels	Revenue por canal
GET	/api/v1/kpis/revenue/categories	Revenue por categoría
Decisiones
Puerto 8001: el simulador usa 8000.

CORS: localhost:5173 para el dashboard.

Sin autenticación en V1: es una demo local.

Schemas Pydantic: valida responses automáticamente.

Dashboard
Stack
Vite 7 + React 19 + TypeScript 5.6 + Tailwind CSS 3 + TanStack Query 5 + Recharts 2 + React Router 7.

Páginas (5)
Página	Propósito	Gráficos
Overview	Snapshot general	Pie canal + Bar categoría
Sales	Serie temporal + canales	Area revenue + Bar canal
Products	Top productos	Bar horizontal + tabla
States	Distribución geográfica	Bar horizontal por grupo
Channels	Online vs Store	Pie + Bar + cards
Responsive
Móvil (375px): 1 columna, sidebar colapsado con hamburguesa.

Tablet (768px): 2 columnas donde aplique.

Desktop (1440px): layout completo, sidebar visible.

Data fetching
TanStack Query con staleTime: 5min y refetchOnWindowFocus: false. Proxy Vite /api → localhost:8001.

Decisiones técnicas
Dos engines de DB
source_engine (5434, solo lectura) y target_engine (5435, lectura/escritura).

UUID + business codes en RAW
PK técnica _raw_id (BIGSERIAL), UUID del origen en _source_id (UNIQUE). Metadata de ingesta para trazabilidad.

Enums como String en RAW/STAGING
Tolerancia. Si el origen agrega valores, RAW no se rompe. Validación con CHECK constraints.

Surrogate keys INTEGER
ROW_NUMBER() con ORDER BY business_key para determinismo. Índices más pequeños, JOINs más rápidos.

SQL puro para transformaciones
text() en lugar del ORM. Más explícito, más rápido, versionable en Git, migrable a dbt en V3.

Tres runners independientes
python -m app.pipeline, python -m app.staging, python -m app.analytical, python -m app.kpis. Cada uno es idempotente y registra en meta.pipeline_runs.

Migración en 3 pasos para columnas nuevas
Cuando se agrega una columna NOT NULL a una tabla con datos: (1) nullable, (2) backfill, (3) NOT NULL.

Limitaciones de V1
Cobertura
Solo 8 entidades RAW cargadas (de las 11 modeladas).

Faltan shipments, suppliers, purchase_orders, returns, inventory_movements.

Faltan facts: fact_inventory, fact_shipments, fact_purchases.

Capas
VALIDATION no implementada (V1.2).

DQ Score no implementado (V1.2).

Rechazos y reconciliación no implementados (V1.2).

Dashboard
Solo 5 páginas de ventas.

Sin filtros globales (fecha, estado, canal).

Sin comparación de periodos.

Orquestación
Sin Airflow. Los runners se corren manualmente.

Sin scheduling automático.

Performance
Sin particionamiento.

Sin clustering.

Sin batch inserts con bulk_save_objects.

Roadmap
V1.1 — Completar entidades y facts
□ Extractor y transformer de shipments
□ Extractor y transformer de suppliers + POs
□ Extractor y transformer de returns
□ Extractor y transformer de inventory_movements
□ fact_inventory, fact_shipments, fact_purchases
V1.2 — Data Quality
□ Capa VALIDATION con reglas por entidad
□ DQ Score con 6 dimensiones
□ Rechazos + reconciliación
□ Alertas en dashboard
V1.3 — Dashboard extendido
□ Páginas: Inventory, Logistics, Procurement, Customers
□ Filtros globales (fecha, estado, canal)
□ Comparación de periodos
□ Exportar a CSV/PDF
V2 — Orquestación
□ Airflow DAG con dependencias
□ Scheduling diario
□ Alertas por fallos
V3 — dbt
□ Migrar transformaciones a dbt
□ Tests de dbt integrados
□ Linaje automático
V4 — Cloud
□ Migrar a BigQuery o Snowflake
□ CI/CD con GitHub Actions
□ Particionamiento y clustering
Conclusión
El data platform implementa el método Google completo:

Ingest everything raw → RAW (8 tablas)

Store in canonical form → STAGING (8 tablas)

Validate early → V1.2

Model for analysis → ANALYTICAL (6 dims + 1 fact)

Serve fast → KPIS (4 tablas) + API (9 endpoints) + Dashboard (5 páginas)

Con idempotencia, incrementalidad, trazabilidad y reproducibilidad verificadas.

Última actualización: 2026-10-22