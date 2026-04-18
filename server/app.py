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


def _parse_float(cell: str) -> Optional[float]:
    s = cell.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _row_is_numeric(row: List[str]) -> bool:
    """True if every non-empty cell parses as a float."""
    for c in row:
        if not c.strip():
            continue
        if _parse_float(c) is None:
            return False
    return True


def parse_csv_numeric(content: str) -> Tuple[List[str], np.ndarray]:
    """
    Read CSV: optional header row (first row with any non-numeric non-empty cell).
    Build float matrix (rows x kept columns) with np.nan for empty/invalid cells.
    A column is kept if it has at least one valid number; invalid cells are skipped (nan).
    """
    reader = csv.reader(io.StringIO(content))
    raw_rows = [list(row) for row in reader if any(c.strip() for c in row)]

    # If there are no rows, return an empty array
    if not raw_rows:
        return [], np.array([]).reshape(0, 0)

    # Ensure all rows have the same length by padding with empty strings
    width = max(len(r) for r in raw_rows)
    for r in raw_rows:
        while len(r) < width:
            r.append("")

    # If there is a header row, use it as the header, and the data rows as the data
    header: Optional[List[str]] = None
    data_rows = raw_rows
    if len(raw_rows) >= 2 and not _row_is_numeric(raw_rows[0]):
        header = raw_rows[0]
        data_rows = raw_rows[1:]

    # If there are no data rows, return an empty array
    if not data_rows:
        return [], np.array([]).reshape(0, 0)

    n_rows = len(data_rows)
    # Per column: any valid number? If so, keep the column
    keep_col = []
    for j in range(width):
        ok = False
        for i in range(n_rows):
            v = _parse_float(data_rows[i][j])
            if v is not None:
                ok = True
                break
        keep_col.append(ok)


    indices = [j for j, k in enumerate(keep_col) if k]
    if not indices:
        return [], np.array([]).reshape(0, 0)

    # Create a list of the names of the columns that are valid (if no header, use Column 1, Column 2, etc.)
    names: List[str] = []
    for j in indices:
        if header is not None and j < len(header):
            label = header[j].strip() or f"Column {j + 1}"
        else:
            label = f"Column {j + 1}"
        names.append(label)

    # Create a matrix of the same length as the number of rows, and the number of columns filled with NaN
    matrix = np.full((n_rows, len(indices)), np.nan, dtype=np.float64)

    # For each column, if the column is valid, add the value to the matrix
    for ci, j in enumerate(indices):
        for i in range(n_rows):
            v = _parse_float(data_rows[i][j])
            if v is not None:
                matrix[i, ci] = v

    return names, matrix
    # Example return:
    # names = ['Column 1', 'Column 2', 'Column 3']
    # matrix = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
    # This means:
    # - The first column has the values 1.0, 4.0, 7.0
    # - The second column has the values 2.0, 5.0, 8.0
    # - The third column has the values 3.0, 6.0, 9.0
    # - The matrix has 3 rows and 3 columns
    # - The matrix is filled with NaN if the column is not valid
    # - The matrix is a numpy array


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> Dict[str, Any]:
    raw = await file.read()
    text = raw.decode("utf-8", errors="replace")
    columns, matrix = parse_csv_numeric(text)

    if matrix.size == 0 or matrix.shape[1] == 0:
        return {"columns": [], "stats": [], "correlation": []}

    stats_list: List[Dict[str, Any]] = []

    # For each column, calculate the mean, median, standard deviation, minimum, and maximum
    for col_idx in range(matrix.shape[1]):
        # Get all the values in the column (vertically), [all_rows, column_index]
        col = matrix[:, col_idx]
        # Get all the valid values in the column (not NaN)
        valid = col[~np.isnan(col)]

        if valid.size == 0:
            # If there are no valid values, add a dictionary with None values for the statistics
            stats_list.append({
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
            })
        else:
            # If there are valid values, add a dictionary with the statistics
            stats_list.append({
                "mean": float(np.mean(valid)),
                "median": float(np.median(valid)),
                "std": float(np.std(valid)),
                "min": float(np.min(valid)),
                "max": float(np.max(valid)),
            })

    # Calculate the correlation matrix (how much two variables are related to each other, for exaample as age increases, the weight increases)
    n_vars = matrix.shape[1]
    complete = matrix[~np.isnan(matrix).any(axis=1)]
    if complete.shape[0] < 2:
        corr = np.eye(n_vars)
    else:
        corr = np.corrcoef(complete.T) # coloumns in csv are features (variables), and corrcoef expects the features to be rows, so we transpose the matrix to get the correlation matrix)
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
