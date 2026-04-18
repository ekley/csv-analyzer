<img width="744" height="649" alt="image" src="https://github.com/user-attachments/assets/a91d43ae-0350-4036-8dc1-c770c2e9834d" />

# CSV Data Analyzer

Small full-stack app: upload a CSV, server computes numeric statistics and a correlation matrix with **NumPy**, and the browser shows tables in plain **HTML + JavaScript** (no frontend framework).

## Stack

- **Backend:** Python 3.8+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [NumPy](https://numpy.org/)
- **Frontend:** Single file, `fetch` + `FormData` to `POST /analyze`

## Project layout

```
server/app.py       # FastAPI app, CORS, /analyze
frontend/index.html # UI
sample.csv          # Example CSV for testing
```

## Setup

```bash
pip install fastapi uvicorn numpy python-multipart
```

## Run the API

From the `server` directory:

```bash
cd server
uvicorn app:app --reload
```

The API listens on **http://127.0.0.1:8000** by default.

## Use the UI

1. Start the server (above).
2. Open `frontend/index.html` in your browser.

If the browser blocks requests from `file://` to localhost, serve the frontend folder instead:

```bash
python -m http.server 8080 --directory frontend
```

Then open **http://127.0.0.1:8080/**.

## API

| Method | Path       | Description                                      |
|--------|------------|--------------------------------------------------|
| `POST` | `/analyze` | Multipart file field `file` (CSV). Returns JSON with `columns`, `stats`, `correlation`. |

Empty or non-numeric cells are skipped per column; correlation uses rows where all kept columns have valid numbers.
