"""End-to-end report determinism and HTTP API behaviour."""
import datetime as dt
import json
import pathlib
import re

import pytest
from fastapi.testclient import TestClient

from app.main import app
from kundali.inputs.places import get_index
from kundali.report.builder import BirthInput, InputError, generate

NOW = dt.datetime(2026, 10, 5, 12, tzinfo=dt.timezone.utc)
client = TestClient(app)


def ktm():
    return get_index().search("Kathmandu")[0].id


def test_report_deterministic():
    b = BirthInput(date="2057-06-19", calendar="BS", time="10:30", place_id=ktm(), name="Test")
    assert json.dumps(generate(b, now=NOW), sort_keys=True) == json.dumps(generate(b, now=NOW), sort_keys=True)


def test_bs_and_ad_inputs_give_same_chart():
    a = generate(BirthInput(date="2057-06-19", calendar="BS", time="10:30", place_id=ktm()), now=NOW)
    b = generate(BirthInput(date="2000-10-05", calendar="AD", time="10:30", place_id=ktm()), now=NOW)
    assert a["chart"] == b["chart"]
    assert a["birth"]["date"]["ad"] == "2000-10-05" and b["birth"]["date"]["bs"] == "2057-06-19"


def test_report_structure():
    r = generate(BirthInput(date="2000-10-05", calendar="AD", time="10:30", place_id=ktm()), now=NOW)
    for key in ("birth", "summary", "chart", "panchanga", "dasha", "gochar", "sadesati", "interpretation",
                "calculation", "disclaimer"):
        assert key in r
    assert len(r["chart"]["planets"]) == 9
    assert r["calculation"]["ephemeris"] == "Swiss Ephemeris"
    assert not any("Moshier" in w for w in r["warnings"])
    assert r["calculation"]["ayanamsha"] == "Lahiri / Chitrapaksha"
    assert r["calculation"]["houseSystem"] == "Whole Sign"
    assert r["summary"]["currentMahadasha"] == "Moon"
    md = r["dasha"]["periods"]
    assert sum(p["status"] == "current" for p in md) == 1
    for section in ("career", "wealth", "marriage", "education", "family", "travel"):
        s = r["interpretation"][section]
        for g in s["strengths"] + s["challenges"]:
            assert g["why"], section
    assert "%" not in json.dumps(r["interpretation"])  # no invented accuracy percentages


def test_approximate_time_labelled():
    r = generate(BirthInput(date="2000-10-05", calendar="AD", time="10:30", place_id=ktm(),
                            time_accuracy="approximate"), now=NOW)
    assert r["warnings"][0].startswith("Birth time reported as approximate")


def test_future_birth_rejected():
    with pytest.raises(InputError):
        generate(BirthInput(date="2030-01-01", calendar="AD", time="10:30", place_id=ktm()), now=NOW)


def test_api_errors():
    r = client.post("/api/kundali", json={"date": "2000-10-05", "time": "10:30"})
    assert r.status_code == 422 and r.json()["detail"]["message"] == "Please select a specific city or location."
    r = client.post("/api/kundali", json={"date": "2000-02-31", "time": "10:30", "placeId": ktm()})
    assert r.status_code == 422 and r.json()["detail"]["field"] == "date"
    r = client.post("/api/kundali", json={"date": "2000-10-05", "time": "", "placeId": ktm()})
    assert r.status_code == 422 and "exact birth time" in r.json()["detail"]["message"]
    r = client.post("/api/kundali", json={"calendar": "BS", "date": "2200-01-01", "time": "10:30", "placeId": ktm()})
    assert r.status_code == 422 and "outside the supported range" in r.json()["detail"]["message"]


def test_api_ok_and_places():
    r = client.get("/api/places", params={"q": "pokh"})
    assert r.json()["results"][0]["name"] == "Pokhara"
    r = client.post("/api/kundali", json={"date": "1990-01-15", "time": "6:45", "meridiem": "AM",
                                          "placeId": ktm(), "asOf": NOW.isoformat()})
    assert r.status_code == 200
    assert r.json()["birth"]["time"] == "06:45:00"
    r = client.post("/api/convert-date", json={"calendar": "BS", "date": "2080-05-19"})
    assert r.json()["ad"] == "2023-09-05"


def test_no_ai_dependencies():
    root = pathlib.Path(__file__).resolve().parents[2]
    pattern = re.compile(r"\b(openai|anthropic|langchain|llama_index|transformers|google\.generativeai|cohere)\b", re.I)
    for path in list(root.rglob("*.py")) + list(root.rglob("package.json")) + list(root.rglob("requirements*.txt")):
        if "node_modules" in path.parts or path.name == "test_report_api.py":
            continue
        assert not pattern.search(path.read_text(errors="ignore")), path


def test_swiss_ephemeris_used_in_worker_threads():
    # API requests run in worker threads; the ephemeris path must be set there too.
    import threading
    out = {}

    def work():
        r = generate(BirthInput(date="2000-10-05", calendar="AD", time="10:30", place_id=ktm()), now=NOW)
        out["eph"] = r["calculation"]["ephemeris"]

    t = threading.Thread(target=work)
    t.start()
    t.join()
    assert out["eph"] == "Swiss Ephemeris"


def test_plain_language_explanation():
    r = generate(BirthInput(date="2000-10-05", calendar="AD", time="10:30", place_id=ktm()), now=NOW)
    e = r["explained"]
    assert len(e["grahas"]) == 9 and len(e["core"]) == 4
    assert [a["key"] for a in e["areas"]][:3] == ["education", "career", "wealth"]
    for a in e["areas"]:
        for p in a["points"]:
            assert p["why"] and "{" not in p["text"]
    edu = " ".join(p["text"] for p in e["areas"][0]["points"])
    assert "spouse" not in edu  # education summary uses education-focused rules
    assert e["period"]["text"].startswith("You are now in the Moon Mahadasha")
    assert len(e["glossary"]) >= 15
    # Personal meaning layer: second-person statements tied to rules.
    assert len(e["glance"]) >= 4 and e["glance"][0].startswith("You ")
    for a in e["areas"]:
        assert a["verdict"] and a["meaning"], a["key"]
        for m in a["meaning"]:
            assert m["why"] and "{" not in m["text"]
    career = e["areas"][1]
    assert career["meaning"][0]["text"].startswith("Your career is strongly linked to income")  # 10th lord in 11th
    assert all(g["forYou"] for g in e["grahas"])
    assert e["period"]["upcoming"][0].startswith("From Aug 2027")


def test_personal_answers():
    r = generate(BirthInput(date="2000-10-05", calendar="AD", time="10:30", place_id=ktm()), now=NOW)
    p = r["interpretation"]["personal"]
    keys = [a["key"] for a in p["answers"]]
    assert keys == ["education", "wealth", "marriage", "career", "children"]
    for a in p["answers"]:
        assert a["answer"] and a["level"] and a["details"]
        assert a["score"] == sum(f["points"] for f in a["factors"]) or a["key"] == "marriage"
    children = p["answers"][4]
    assert "does not predict the number or sex" in children["details"][0]
    career = p["answers"][3]
    assert career["level"] in ("Top of field", "Senior leadership", "Established professional", "Steady rise")
