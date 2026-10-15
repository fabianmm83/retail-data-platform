# Arquitectura — Retail Data Platform

Documento técnico sobre las decisiones de diseño del pipeline de datos.

---

## Tabla de contenido

1. [Visión general](#visión-general)
2. [Filosofía de diseño](#filosofía-de-diseño)
3. [Capas del pipeline](#capas-del-pipeline)
4. [Estructura de schemas](#estructura-de-schemas)
5. [Modelos RAW](#modelos-raw)
6. [Ingesta incremental](#ingesta-incremental)
7. [Idempotencia](#idempotencia)
8. [Trazabilidad](#trazabilidad)
9. [Manejo de errores](#manejo-de-errores)
10. [Decisiones técnicas](#decisiones-técnicas)
11. [Limitaciones de V1](#limitaciones-de-v1)
12. [Roadmap](#roadmap)

---

## Visión general

El data platform consume datos del simulador y los transforma en analítica. Sigue el **método Google** de data engineering: 5 principios fundamentales.

```text
1. Ingest everything raw       → capa RAW
2. Store in a canonical form   → capa STAGING
3. Validate early              → capa VALIDATION
4. Model for analysis          → capa ANALYTICAL
5. Serve fast                  → capa KPIs + API
Todas las operaciones del pipeline son:

Idempotentes: correr dos veces no duplica datos.

Incrementales: solo procesa lo nuevo.

Trazables: cada corrida deja un registro.

Recuperables: si falla, hace rollback y se puede reintentar.

Filosofía de diseño
Principio 1 — RAW como fuente de verdad
La capa RAW es una copia fiel de la fuente. Nunca se modifica manualmente. Si algo falla en las capas siguientes, se puede reprocesar desde RAW.

Principio 2 — Idempotencia por diseño
Todo loader usa UPSERT por _source_id. Correr el pipeline dos veces con los mismos datos no duplica nada.

Principio 3 — Ingesta incremental
El pipeline usa watermarks para traer solo los datos nuevos. No reprocesa todo cada vez.

Principio 4 — Trazabilidad completa
Cada corrida tiene un run_id. Cada fila insertada guarda su _ingestion_run_id. Se puede reconstruir "qué filas vinieron de qué corrida".

Principio 5 — Transaccionalidad
Cada entidad se ingesta en una transacción. Si falla, hace rollback y marca el run como FAILED.

Capas del pipeline
text
INGESTION → RAW → VALIDATION → STAGING → ANALYTICAL → KPIs → DASHBOARD
Estado actual
Capa	Estado
INGESTION	✅ funcional (3 entidades)
RAW	✅ funcional (11 tablas, 3 pobladas)
VALIDATION	⏳ pendiente
STAGING	⏳ pendiente
ANALYTICAL	⏳ pendiente
KPIs	⏳ pendiente
DASHBOARD	⏳ pendiente
Estructura de schemas
PostgreSQL destino (retail_analytics) organiza las tablas en 6 schemas:

text
raw           ← copia fiel de la fuente
staging       ← limpio y tipado
analytical    ← modelo estrella (dims + facts)
kpis          ← métricas precalculadas
dq            ← data quality (rechazos, scores)
meta          ← control del pipeline
Por qué schemas separados:

Aislamiento lógico: cada capa con su propósito.

Control de acceso: se pueden otorgar permisos por schema.

Claridad: al ver el nombre de una tabla, sabes qué capa es.

Flexibilidad: cada schema puede tener políticas de retención distintas.

Modelos RAW
Estructura común
Todas las tablas RAW heredan de RawMixin:

python
class RawMixin:
    _raw_id: Mapped[int]           # BIGSERIAL PK (técnico)
    _source_id: Mapped[str]        # UUID del origen (UNIQUE)
    _ingested_at: Mapped[datetime] # timestamp real
    _ingestion_run_id: Mapped[str] # run_id de la ingesta
    _source_table: Mapped[str]     # tabla origen
Por qué enums como string
En la fuente, los campos enum son tipos nativos de PostgreSQL. En RAW, se guardan como String.

Razón: RAW debe ser lo más tolerante posible. Si el origen agrega un nuevo valor al enum, RAW no debe romperse.

Implementación: en los extractores usamos ::text para castear los enums a string en la query.

Por qué metadata adicional
Cinco columnas adicionales:

_raw_id: PK técnica (BIGSERIAL). No es el UUID del origen.

_source_id: UUID del origen. Se usa para UPSERT idempotente.

_ingested_at: cuándo se cargó.

_ingestion_run_id: qué corrida del pipeline lo trajo.

_source_table: de qué tabla origen vino.

Permiten:

Reprocesar sin duplicar.

Auditar qué llegó y cuándo.

Filtrar por corrida específica.

Ingesta incremental
Watermark
Un watermark por entidad. Registra hasta dónde se ha ingestado.

text
meta.watermarks
├── entity_name         ('orders')
├── last_watermark_date (2026-05-15)
├── last_watermark_id   (ORD-2026-003421)
├── last_run_at         (timestamp real)
├── rows_last_run       (47)
└── status              (SUCCESS | FAILED | RUNNING)
Modos de ingesta
Full load:

sql
SELECT * FROM customers ORDER BY customer_code
Se usa para entidades que:

No cambian durante la simulación.

Son pocas (10,000 filas o menos).

No tienen un timestamp natural.

Incremental:

sql
SELECT * FROM orders
WHERE order_date > :watermark_date
   OR (order_date = :watermark_date AND order_number > :watermark_id)
ORDER BY order_date, order_number
Se usa para entidades que:

Crecen con el tiempo.

Tienen una fecha o timestamp natural.

Son grandes.

El "truco" del watermark_id vacío
Cuando no hay watermark previo, watermark_id = None. PostgreSQL falla con:

text
AmbiguousParameter: could not determine data type of parameter $2
Solución: usar string vacío "" en lugar de NULL.

python
wid = watermark_id if watermark_id is not None else ""
Y la query:

sql
WHERE order_date > :wdate
   OR (order_date = :wdate AND order_number > :wid)
order_number > '' siempre es true (cualquier string es mayor que vacío). Resultado: en la primera corrida se trae todo lo que tenga order_date >= wdate.

Idempotencia
UPSERT por _source_id
python
stmt = pg_insert(model).values(enriched)
update_cols = {
    col.name: stmt.excluded[col.name]
    for col in model.__table__.columns
    if col.name not in ("_raw_id", "_ingested_at")
}
stmt = stmt.on_conflict_do_update(
    index_elements=["_source_id"],
    set_=update_cols,
)
Por qué funciona:

Si _source_id no existe → INSERT.

Si _source_id ya existe → UPDATE de todos los campos excepto _raw_id y _ingested_at.

Verificación
text
Corrida 1:  extraídas 188 filas, 188 procesadas
Corrida 2:  extraídas 0 filas (watermark avanzado)
sql
SELECT COUNT(*) FROM raw.orders;  -- 188 (no duplicado)
Trazabilidad
run_id
Formato: ING-YYYYMMDD-HHMMSS-8hex

Ejemplo: ING-20261015-201927-bd7cf0f2

Cada corrida del pipeline genera uno. Se guarda en:

meta.pipeline_runs.run_id: registro de la corrida.

raw.*._ingestion_run_id: cada fila insertada.

pipeline_runs
text
meta.pipeline_runs
├── run_id              (ING-...)
├── started_at
├── finished_at
├── status              (RUNNING | SUCCESS | FAILED)
├── entities_processed  (CSV)
├── rows_ingested       (total)
└── error_message       (si falla)
Consultas útiles
sql
-- ¿Qué filas trajo la corrida X?
SELECT * FROM raw.orders WHERE _ingestion_run_id = 'ING-...';

-- ¿Cuándo fue la última ingesta exitosa de orders?
SELECT * FROM meta.pipeline_runs
WHERE entities_processed LIKE '%orders%'
  AND status = 'SUCCESS'
ORDER BY finished_at DESC LIMIT 1;
Manejo de errores
Transaccionalidad
Cada entidad se ingesta en una transacción. Si falla:

target_db.rollback() revierte los cambios.

meta.pipeline_runs.status = 'FAILED'.

meta.pipeline_runs.error_message guarda la causa.

La excepción se propaga al caller.

Estado de watermarks
RUNNING: cuando empieza la ingesta.

SUCCESS: cuando termina exitosamente.

FAILED: cuando algo falla.

Si el proceso se interrumpe (Ctrl+C), el watermark queda en RUNNING y hay que limpiarlo:

sql
UPDATE meta.watermarks SET status = 'FAILED' WHERE status = 'RUNNING';
UPDATE meta.pipeline_runs SET status = 'FAILED' WHERE status = 'RUNNING';
Reintentos
Como la ingesta es idempotente, se puede reintentar sin problemas:

bash
python -m app.pipeline --entities orders
Si falla a la mitad, el próximo intento retoma desde el último watermark exitoso.

Decisiones técnicas
UUID v4 en RAW como String
En la fuente, los IDs son UUID. En RAW los guardamos como UUID(as_uuid=False) (string).

Por qué string:

RAW debe ser tolerante.

Si el origen cambia de UUID a otro tipo, RAW no se rompe.

Es más fácil de inspeccionar.

Enums como String
Igual que arriba. RAW tolera cualquier valor, incluso inválidos.

Dos engines de DB
python
source_engine = create_engine(settings.source_database_url)  # 5434
target_engine = create_engine(settings.target_database_url)  # 5435
Por qué dos engines:

El origen es solo lectura.

El destino es lectura/escritura.

Se pueden aplicar políticas distintas (pool size, timeouts).

Nunca se escribe al origen desde el data platform.

Modelos de origen locales
El data platform no importa los modelos del simulador. Define sus propios modelos en app/ingestion/source_models.py.

Por qué:

Desacoplamiento: dos repos independientes.

Control: si el simulador cambia, solo el origen se ve afectado.

Claridad: los modelos de origen son explícitamente read-only.

SQL puro para extractores
Los extractores usan text() en lugar del ORM.

Por qué:

Permite ::text para castear enums sin complicaciones.

Es más rápido para bulk selects.

Más explícito (se ve el SQL).

Más fácil de optimizar.

Limitaciones de V1
Cobertura
Solo 3 de las 11 tablas RAW están implementadas en el pipeline.

Las otras 8 (products, variants, states, locations, shipments, carriers, categories, inventory_movements) están creadas pero vacías.

Capas
VALIDATION, STAGING, ANALYTICAL, KPIs, DASHBOARD no están implementadas.

Orquestación
Sin Airflow. El pipeline se corre manualmente vía CLI.

Performance
Sin batch inserts con bulk_save_objects.

Sin paralelización.

Sin particionamiento.

Data Quality
Sin reglas de validación.

Sin DQ Score.

Sin tabla de rechazos.

Roadmap
V1.1 — Completar 3 entidades prioritarias
□ BLOQUE 5: STAGING (limpieza + tipado)
□ BLOQUE 6: ANALYTICAL (dims + facts)
□ BLOQUE 7: KPIs
□ BLOQUE 8: API intermedia
□ BLOQUE 9: Dashboard React
V1.2 — Escalar entidades
□ Agregar extractores para las 8 entidades restantes.
□ Optimizar con batches.
V1.3 — Data Quality
□ Implementar capa VALIDATION.
□ Reglas por entidad.
□ DQ Score.
□ Rechazos y reconciliación.
V2 — Orquestación
□ Airflow para orquestar el pipeline.
□ DAG con dependencias entre entidades.
□ Scheduling automático.
V3 — dbt
□ Migrar transformaciones a dbt.
□ Tests de dbt.
□ Documentación de linaje.
V4 — Cloud
□ Migrar a BigQuery o Snowflake.
□ Particionamiento y clustering.
□ CI/CD con GitHub Actions.
Conclusión
El data platform implementa el método Google de data engineering:

Ingest everything raw: RAW es copia fiel.

Store in a canonical form: STAGING impone un formato único.

Validate early: VALIDATION rechaza datos malos.

Model for analysis: ANALYTICAL usa star schema.

Serve fast: KPIs precalculados + API + Dashboard.

El pipeline es:

Idempotente: correr dos veces no duplica.

Incremental: watermarks evitan reprocesar.

Trazable: run_id en cada fila.

Recuperable: rollback y reintento.

Es la base sólida sobre la cual se construye el resto del ecosistema analítico.

Última actualización: 2026-10-15
