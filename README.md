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

## Run everything from the project root

Starts the API (`uvicorn` in `server/`) and the static UI (`python -m http.server` on port **5500** in `frontend/`):

```bash
python run_dev.py
```

- **API:** http://127.0.0.1:8000  
- **UI:** http://127.0.0.1:5500/  

Stop both with **Ctrl+C** in that terminal.

## Run the API only

From the `server` directory:

```bash
cd server
uvicorn app:app --reload
```

The API listens on **http://127.0.0.1:8000** by default.

## Use the UI

1. Start the server (see above or `run_dev.py`).
2. Open `frontend/index.html` in your browser, or use the URL from `run_dev.py`.

If the browser blocks requests from `file://` to localhost, serve the frontend folder instead:

```bash
python -m http.server 5500 --directory frontend
```

Then open **http://127.0.0.1:5500/** (use another port if 5500 is busy).

## API

| Method | Path       | Description                                      |
|--------|------------|--------------------------------------------------|
| `POST` | `/analyze` | Multipart file field `file` (CSV). Returns JSON with `columns`, `stats`, `correlation`. |

Empty or non-numeric cells are skipped per column; correlation uses rows where all kept columns have valid numbers.
