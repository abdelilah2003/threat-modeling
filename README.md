# Enterprise RAG API

## Run locally

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --app-dir . --host 0.0.0.0 --port 8000
```

If you see `POST /ask` returning `404 Not Found`, you are likely importing a different `app` module from your environment.
Using `--app-dir .` forces uvicorn to load this repository's `app/` package.

Alternative (collision-safe):

```bash
python -m uvicorn main:app --app-dir . --host 0.0.0.0 --port 8000
```

## Verify

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the password policy?"}'
```
