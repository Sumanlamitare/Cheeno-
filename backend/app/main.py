"""HTTP API and static frontend server.

Stateless: birth data is processed in memory for the duration of a request
and never stored or logged.
"""

from __future__ import annotations

import datetime as dt
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from kundali.inputs.calendar import CalendarError, resolve_date
from kundali.inputs.places import PlaceError, get_index, place_from_coordinates
from kundali.jyotish.yogas import yoga_definitions
from kundali.report.builder import BirthInput, InputError, generate
from kundali.rules.nakshatra import nakshatra_catalogue

log = logging.getLogger("kundali")


@asynccontextmanager
async def lifespan(_app):
    get_index()  # load the offline place index once at startup
    yield


app = FastAPI(
    title="Janma Kundali API",
    description="Deterministic Vedic (Jyotish) birth chart calculation and rule-based interpretation.",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
origins = [o for o in os.environ.get("CORS_ORIGINS", "").split(",") if o]
if origins:
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["*"])


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Frame-Options", "DENY")
    if request.url.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")
    return response


class KundaliRequest(BaseModel):
    name: str | None = Field(None, max_length=80)
    calendar: str = Field("AD", pattern="^(AD|BS)$")
    date: str = Field(..., max_length=12)
    time: str = Field(..., max_length=10)
    meridiem: str | None = Field(None, pattern="^(AM|PM)$")
    timeAccuracy: str = Field("exact", pattern="^(exact|approximate)$")
    placeId: str | None = Field(None, max_length=40)
    latitude: float | None = None
    longitude: float | None = None
    placeLabel: str | None = Field(None, max_length=80)
    utcOffsetOverride: float | None = None
    asOf: str | None = Field(None, description="ISO datetime used as 'now' (for testing); defaults to current time")


class DateRequest(BaseModel):
    calendar: str = Field(..., pattern="^(AD|BS)$")
    date: str = Field(..., max_length=12)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/places")
def places(q: str = Query(..., min_length=2, max_length=60), limit: int = Query(10, ge=1, le=20)):
    return {"results": [p.to_dict() for p in get_index().search(q, limit)]}


@app.get("/api/places/coordinates")
def coordinates(lat: float, lon: float):
    try:
        return place_from_coordinates(lat, lon).to_dict()
    except PlaceError as e:
        raise HTTPException(status_code=422, detail={"field": "place", "message": str(e)})


@app.post("/api/convert-date")
def convert_date(req: DateRequest):
    try:
        info = resolve_date(req.calendar, req.date)
    except CalendarError as e:
        raise HTTPException(status_code=422, detail={"field": "date", "message": str(e)})
    return info["display"]


@app.post("/api/kundali")
def kundali(req: KundaliRequest):
    now = None
    if req.asOf:
        try:
            now = dt.datetime.fromisoformat(req.asOf)
        except ValueError:
            raise HTTPException(status_code=422, detail={"field": "asOf", "message": "asOf must be an ISO datetime."})
    b = BirthInput(
        date=req.date, calendar=req.calendar, time=req.time, meridiem=req.meridiem,
        time_accuracy=req.timeAccuracy, name=req.name, place_id=req.placeId, latitude=req.latitude,
        longitude=req.longitude, place_label=req.placeLabel, utc_offset_override=req.utcOffsetOverride,
    )
    try:
        return generate(b, now=now)
    except InputError as e:
        raise HTTPException(status_code=422, detail={"field": e.field, "message": e.message})
    except Exception:  # never echo birth data into logs
        log.exception("Kundali generation failed")
        raise HTTPException(status_code=500, detail={"field": None, "message": "The chart could not be calculated."})


@app.get("/api/reference/nakshatras")
def nakshatras():
    return {"nakshatras": nakshatra_catalogue()}


@app.get("/api/reference/yogas")
def yogas():
    return {"yogas": yoga_definitions()}


# ---------------------------------------------------------------------------
# Static frontend (built React app)
# ---------------------------------------------------------------------------

DIST = Path(os.environ.get("FRONTEND_DIST", Path(__file__).resolve().parents[2] / "frontend" / "dist"))

if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        if path.startswith("api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        candidate = (DIST / path).resolve()
        if path and candidate.is_file() and DIST.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")
