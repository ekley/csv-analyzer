"""
Run API + static frontend from the project root (no need to cd into server/ or frontend/).

Usage (from repo root):
  python run_dev.py
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "server"
FRONTEND_DIR = ROOT / "frontend"
HTTP_PORT = "5500"


def main() -> None:
    procs: list[subprocess.Popen] = [
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--reload"],
            cwd=str(SERVER_DIR),
        ),
        subprocess.Popen(
            [sys.executable, "-m", "http.server", HTTP_PORT],
            cwd=str(FRONTEND_DIR),
        ),
    ]

    print("API (FastAPI):  http://127.0.0.1:8000")
    print("UI (static):    http://127.0.0.1:%s/" % HTTP_PORT)
    print("Press Ctrl+C to stop both.\n")

    try:
        while True:
            if all(p.poll() is not None for p in procs):
                break
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        for p in procs:
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == "__main__":
    main()
