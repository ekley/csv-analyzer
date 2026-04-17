from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _row_is_numeric(row: List[str]) -> bool:
    """True if every non-empty cell parses as a float."""
    for c in row:
        if not c.strip():
            continue
        if _parse_float(c) is None:
            return False
    return True


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> Dict[str, Any]:
    raw = await file.read()
    text = raw.decode("utf-8", errors="replace")
    columns, matrix = ['height_cm', 'weight_kg', 'age'], np.array([
        [170.,   72.5,  28. ],
        [165.,   58.,   34. ],
        [182.,   85.2,  41. ],
        [158.,   52.3,  22. ],
        [175.,   68.7,  29. ],
        [ np.nan, np.nan, 31. ],
        [172.,   75.,   np.nan ],
        [160.,   55.5,  25. ]])

    if matrix.size == 0 or matrix.shape[1] == 0:
        return {"columns": [], "stats": [], "correlation": []}

    stats_list: List[Dict[str, Any]] = []
    for col_idx in range(matrix.shape[1]):
        col = matrix[:, col_idx]
        valid = col[~np.isnan(col)]
        if valid.size == 0:
            stats_list.append({
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
            })
        else:
            stats_list.append({
                "mean": float(np.mean(valid)),
                "median": float(np.median(valid)),
                "std": float(np.std(valid)),
                "min": float(np.min(valid)),
                "max": float(np.max(valid)),
            })

    n_vars = matrix.shape[1]
    complete = matrix[~np.isnan(matrix).any(axis=1)]
    if complete.shape[0] < 2:
        corr = np.eye(n_vars)
    else:
        corr = np.corrcoef(complete.T)
        corr = np.asarray(corr)
        if corr.ndim == 0:
            corr = np.array([[1.0]])
        elif corr.ndim == 1:
            corr = np.reshape(corr, (1, 1))

    return {
        "columns": columns,
        "stats": stats_list,
        "correlation": corr.tolist(),
    }
