# SQL Agent

A lightweight text-to-SQL agent that translates natural language into safe, validated SQL using schema grounding and strict guardrails.

---

## 📁 Initial structure
```bash
sql-agent/
│
├── README.md
├── .env.example
├── pyproject.toml / requirements.txt
├── dockerfile
├── src/
│ ├── sql_agent/
│ │ ├── validator.py
│ │ ├── executor.py
│ │ ├── agent.py
│ │ └── schema_reflect.py
│ ├── obs/
│ │ ├── metrics.py
│ │ ├── tracing.py
│ │ └── mlflow_log.py
│ ├── service/
│ │ └── api.py
│ └── utils/
│ └── io.py
│
├── ui/
│ ├── streamlit_app.py
│ └── (optional) web/React console/
│
├── tests/
│ ├── test_validator.py
│ ├── test_end_to_end.py
│ └── test_executor.py
└── .github/
└── workflows/
└── ci.yml
```


---

## ⚙️ Core Stack

| Layer | Tooling |
|-------|----------|
| DB | DuckDB (local) / Postgres via SQLAlchemy |
| Validation | sqlglot |
| Orchestration | LangGraph |
| API | FastAPI |
| UI | Streamlit or React |
| Observability | Prometheus + OpenTelemetry |
| Eval logging | MLflow |
| Tests | pytest + Postgres service CI |

---

## 🚨 Known Risks & Mitigations

### Unsafe SQL
- **Risk:** Model outputs DDL/DML.  
- **Mitigation:** sqlglot validation: SELECT-only; auto-LIMIT injection; blacklist forbidden tables.

### Incorrect SQL / Schema Drift
- **Risk:** Joins or columns don’t exist.  
- **Mitigation:** Schema reflection + allowlist; validation rejects hallucinated elements.

### Runaway Queries
- **Risk:** Full scans or long execution time.  
- **Mitigation:** Timeout, row cap, EXPLAIN path; sample mode for large tables.

### Prompt Injection via Data
- **Risk:** Text in tables steering model.  
- **Mitigation:** Sanitize inputs, ignore meta instructions, strip control tokens.

### Data Leakage / PII Exposure
- **Risk:** Returning sensitive fields.  
- **Mitigation:** Column allowlist; results scrubber; redaction before logging.

### Ambiguity / Low Confidence
- **Risk:** Underspecified NL query.  
- **Mitigation:** Confidence threshold; ask-clarify cycle before execution.

### Lack of Auditability
- **Risk:** Hard to reproduce runs.  
- **Mitigation:** Structured logs (NL → SQL → result hash); MLflow + OTel traces.

---

## 🧠 Quick Start

```bash
uv sync
uv run python -m src.service.api
# or run Streamlit UI
uv run streamlit run ui/streamlit_app.py
```

## 📊 Observability

- Prometheus metrics: sql_exec_latency_seconds, validator_failures_total
- OTel spans: describe_schema, generate_sql, validate_sql, execute_sql
- MLflow logs: success rate, latency per schema

## Tech Stack (short version)
- Python 3.11

- LangGraph (tool orchestration)

- DuckDB / Postgres via SQLAlchemy

- sqlglot (SQL validation + transpile)

- FastAPI service layer

- Streamlit / React UI (choose one)

- Prometheus + OpenTelemetry (metrics / tracing)

- MLflow (success / latency logs)

- pytest, GitHub Actions, Docker, uv / Poetry (tooling)


