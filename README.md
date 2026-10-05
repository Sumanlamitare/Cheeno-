# Janma Kundali · जन्म कुण्डली

A web application that calculates and interprets a traditional Nepali **Janma Kundali / Janma Patrika / China**,
deterministically:

```
Birth date + time + place
        ↓
Swiss Ephemeris (astronomy)
        ↓
Sidereal / Lahiri / Whole Sign (Jyotish calculations)
        ↓
Explicit rule library (interpretation)
        ↓
Complete Kundali in the browser, printable as PDF
```

* **No AI / LLM.** No AI SDKs, APIs, prompts or generated text. Every sentence comes from a written rule.
* **No database, no accounts.** Each request is calculated on demand and nothing is stored.
* **Deterministic.** The same birth data and the same reference date always give the same report.
* **Transparent.** Every conclusion has a *Why?* listing the exact placements that triggered it.

---

## Features

| Area | What is calculated |
|---|---|
| Input | AD or **Bikram Sambat** date (proper table-based conversion, BS 1975–2100), 12/24-hour time with seconds, exact/approximate flag, offline worldwide place search (~34,000 cities + Nepal district HQs), manual coordinates, optional UTC-offset override |
| Time | Historical IANA timezones and DST; birthplace Local Mean Time before standard time (including pre-1920 Nepal and pre-1906 South Asia); warnings for skipped/repeated DST times |
| Grahas | Sun–Saturn, Rahu/Ketu (mean node): sidereal longitude, sign, D°M'S", house, nakshatra, pada, retrograde, combustion, exaltation/debilitation, own sign, moolatrikona, five-fold friendships |
| Charts | North Indian D1, D9, D10; all 16 Parashari vargas (D1–D60) under *Advanced* |
| Strength | Full **Shadbala** (Sthana, Dig, Kala, Chesta, Naisargika, Drik, plus Yuddha), with the method documented |
| Drishti | Parashari sign aspects (7th for all; Mars 4/8, Jupiter 5/9, Saturn 3/10) |
| Panchanga | Tithi, Vara (from Hindu sunrise), Nakshatra, Yoga, Karana, lunar month (Purnimanta/Amanta, Adhika), Ishta Kala in ghati-pala |
| Dasha | Vimshottari Mahadasha → Antardasha → Pratyantardasha, current periods, visual life timeline with year selector |
| Gochar | Current transits from the natal Moon with Vedha; upcoming Jupiter/Saturn/Rahu/Ketu sign changes |
| Sade Sati | All lifetime cycles with exact phase dates; Dhaiya (Kantaka/Ashtama Shani) |
| Yogas | 19 structured yoga rules: Raja (Kendra-Trikona), Yogakaraka, Dharma-Karmadhipati, Dhana, Lakshmi, Gaja Kesari, Budha-Aditya, Chandra-Mangala, the five Mahapurusha, Viparita (Harsha/Sarala/Vimala), Neecha Bhanga, Adhi, Sunapha/Anapha/Durudhara, Vesi/Vasi/Ubhayachari, Amala, Vasumati, Saraswati, Parivartana, Shakata |
| Doshas | Mangal (from Lagna, Moon and Venus, with mitigations), Kaal Sarp (labelled disputed, exact rule stated), Kemadruma (with cancellations), Gandamula, Grahana |
| Readings | Lagna & core nature, Janma Rashi & Nakshatra, the 12 Bhavas, career, wealth, education, love & marriage, family, travel/relocation, children, health (non-medical), current Dasha, D9, D10 |

## Architecture

```
backend/
  kundali/
    inputs/      Layer 1: BS↔AD calendar, time parsing, historical timezones, offline places
    astro/       Layer 2: Swiss Ephemeris wrapper (no astronomy written by hand)
    jyotish/     Layer 3: chart, dignity, drishti, vargas, panchanga, dasha, gochar,
                 sade sati, shadbala, yogas, doshas
    rules/       Layer 4: rule engine + rule modules
      engine.py    declarative conditions, weighting, grouping, synthesis
      data/        classical tables (Bhavesha phala 12×12, Graha-Bhava phala 9×12,
                   27 nakshatras, lagnas, panchanga, transits, yogas/doshas)
      lagna.py houses.py nakshatra.py planets.py career.py wealth.py marriage.py
      education.py family.py travel.py children.py health.py dasha.py transits.py
      yogas.py doshas.py vargas.py panchanga.py
    report/      assembles the JSON report
    config.py    calculation settings (ayanamsha, nodes, dasha year) and weights
  app/main.py    FastAPI: /api/places, /api/convert-date, /api/kundali, static frontend
  ephe/          Swiss Ephemeris data files (1800–2400 AD)
  tests/         363 automated tests
frontend/        Layer 5: React + TypeScript (Vite)
```

The calculation layers never import the rule layer, and the rules never call the ephemeris. A database, user
accounts, Kundali matching or other features can be added on top without touching the engines.

### How a reading is built (Layer 4)

Each rule is data:

```python
rule("career_L10_in_11", "career", "career.gains", "major", "positive",
     [{"t": "in_house", "p": "L10", "h": 11}],
     "Traditional Jyotish associates the 10th lord in the 11th with career activity connected with gains, ...",
     "10th lord in 11th house", subject="L10")
```

1. Every rule in a category is evaluated against the chart. The conditions also produce the *Why?* reasons
   (for example "10th lord Sun is placed in the 11th house (Virgo)").
2. The weight comes from the tier (major 100, strong 70, moderate 40, minor 20; configurable in `config.py`). It is
   then adjusted if the subject planet is strong or weak (convention documented in `engine.py`).
3. Matches are grouped by theme. The strongest match is the main statement, similar ones become supporting
   points, and repeats count for less (diminishing weight).
4. Strengths and challenges are kept separate, and contradictions are never hidden. The overall statement comes
   from the weighted balance using fixed template bands.
5. Timing windows are the Antardasha periods whose lords signify that area of life (plus Jupiter's transit
   for marriage).

There are roughly 490 declarative domain rules, 144 Bhavesha rules, 108 Graha-Bhava rules, 27 nakshatra profiles,
19 yoga evaluators and 5 dosha evaluators.

## Calculation conventions

| Setting | Value |
|---|---|
| Zodiac | Sidereal (Nirayana) |
| Ayanamsha | Lahiri / Chitrapaksha (`SIDM_LAHIRI`) |
| Houses | Whole Sign |
| Ephemeris | Swiss Ephemeris files `sepl_18`, `semo_18` (1800–2400 AD) |
| Rahu/Ketu | Mean node (switch to the true node in `config.py`) |
| Sunrise | Hindu rising: centre of the disc, no refraction |
| Vimshottari year | 365.25 days |
| Node dignity | Rahu exalted in Taurus, Ketu in Scorpio (one tradition; stated in code) |
| Kaal Sarp | All seven grahas strictly within one Rahu–Ketu half by longitude |
| Mangal Dosha | Mars in 1, 2, 4, 7, 8, 12 from the Lagna, Moon and Venus, with listed mitigations |

Where traditions differ, the code says which convention it uses. No accuracy percentage is ever shown.

## Running locally

Requirements: Python 3.11+, Node 20+.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000

# Frontend (second terminal)
cd frontend
npm install
npm run dev          # http://localhost:5173 (proxies /api to :8000)
```

Production-style single process: run `npm run build` in `frontend/`, then
`uvicorn app.main:app --port 8000` in `backend/`. The API serves the built site at http://localhost:8000.

### Tests

```bash
cd backend && pytest -q
```

The tests cover BS↔AD anchors (Nepali New Years 2080–2082), historical offsets (Nepal +5:30 → +5:45 in 1986,
New York/Sydney DST, wartime India), LMT handling, and known astronomical events: Makar and Mesh Sankranti 2024,
the full Moon of 25 Jan 2024, the eclipse new Moon of 8 Apr 2024, Mercury and Jupiter retrogrades, Saturn and
Jupiter sign changes, and Rahu in Pisces in 2024. They also cover Lahiri ayanamsha at J2000, Kathmandu sunrise,
M. K. Gandhi's published Libra Lagna and Cancer Moon, and Durga Ashtami 2000 for the Panchanga. Further checks:
nakshatra/pada boundaries, Drishti, dignities, every varga formula, Vimshottari balances and sub-period
proportions, Sade Sati dates for Aquarius and Sagittarius Moons, and Shadbala ranges. Yoga detection is
property-tested against its definitions on 150 charts. Rule-library completeness, report determinism, API errors,
and a scan for AI dependencies are also tested.

## Deployment

The repository ships a two-stage `Dockerfile`: it builds the frontend, then runs a slim Python image as a non-root
user, with a health check at `/api/health`.

```bash
docker build -t janma-kundali .
docker run -p 8000:8000 janma-kundali
```

* **Render**: *New → Blueprint* and pick this repository (`render.yaml` is included).
* **Railway / Fly.io / Google Cloud Run / any container host**: deploy the Dockerfile. The app listens on
  `$PORT` (default 8000). `WEB_CONCURRENCY` sets the number of worker processes (default 2).
* Optional: `CORS_ORIGINS` (comma-separated) if the frontend is hosted on a different origin.

No secrets, API keys or database are needed. Each worker uses about 150–250 MB of RAM because of the offline
place and timezone data.

## Privacy

Birth details are processed in memory for one request and never stored or logged. API responses are sent with
`Cache-Control: no-store`. There are no accounts, cookies, analytics or third-party calls. The only external
resource is the Google Fonts stylesheet; self-host the fonts to remove it.

## Licence

The Swiss Ephemeris is distributed by Astrodienst AG under the **AGPL-3.0** (or a paid commercial licence). This
project is therefore licensed under the **GNU AGPL-3.0** (see `LICENSE`). If you run a modified version as a
public web service, you must offer its source code to users. For a closed-source product, buy the Swiss Ephemeris
professional licence from Astrodienst first.

Place data © GeoNames (CC BY 4.0). Timezone data: IANA tz database.

## Disclaimer

Jyotish is a traditional astrological system. Its interpretations are cultural and spiritual frameworks and are
not scientifically validated predictions. This reading should not replace professional medical, financial, legal
or other expert advice.
