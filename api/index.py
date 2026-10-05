"""Vercel serverless entrypoint: exposes the FastAPI app from backend/."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
os.environ.setdefault("KUNDALI_EPHE_PATH", os.path.join(ROOT, "backend", "ephe"))

from app.main import app  # noqa: E402,F401
