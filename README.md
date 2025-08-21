# Pikszis MVP

A minimal FastAPI application backed by Supabase.  It provides a random question hub and questionnaire runner for the Pikszis project.

## Quick start

```bash
# install deps
pip install -r requirements.txt  # or using poetry/uv

# run dev server
uvicorn app.main:app --reload
```

Copy `.env.example` to `.env` and fill in the Supabase keys before running.

### Docker

```bash
make dev      # run using docker-compose
make import   # run CSV importer
```

### Testing

```
make test
```