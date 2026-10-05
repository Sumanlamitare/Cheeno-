import { useEffect, useMemo, useRef, useState } from "react";
import { ApiError, convertDate, placeFromCoordinates, searchPlaces, type KundaliRequest } from "../api";
import { AD_MONTHS, BS_MONTHS, fmtLatLon } from "../format";
import type { DualDate, Place } from "../types";

interface Props {
  onSubmit: (req: KundaliRequest) => void;
  loading: boolean;
  serverError: { message: string; field: string | null } | null;
}

type Errors = Partial<Record<"date" | "time" | "place" | "form", string>>;

function pad(n: string, len = 2) {
  return n.padStart(len, "0");
}

export default function BirthForm({ onSubmit, loading, serverError }: Props) {
  const [name, setName] = useState("");
  const [calendar, setCalendar] = useState<"AD" | "BS">("AD");
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [timeFormat, setTimeFormat] = useState<"12" | "24">("12");
  const [hour, setHour] = useState("");
  const [minute, setMinute] = useState("");
  const [second, setSecond] = useState("");
  const [meridiem, setMeridiem] = useState<"AM" | "PM">("AM");
  const [accuracy, setAccuracy] = useState<"exact" | "approximate">("exact");
  const [unknownTime, setUnknownTime] = useState(false);

  const [placeMode, setPlaceMode] = useState<"search" | "coords">("search");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Place[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [place, setPlace] = useState<Place | null>(null);
  const [activeIdx, setActiveIdx] = useState(-1);
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [coordPlace, setCoordPlace] = useState<Place | null>(null);
  const [offsetOverride, setOffsetOverride] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [dual, setDual] = useState<DualDate | null>(null);
  const [errors, setErrors] = useState<Errors>({});
  const searchAbort = useRef<AbortController | null>(null);

  const isoDate = year.length === 4 && month && day ? `${year}-${pad(month)}-${pad(day)}` : "";

  // Live calendar conversion so the user can verify the interpreted date.
  useEffect(() => {
    setDual(null);
    if (!isoDate) return;
    const ctrl = new AbortController();
    const t = setTimeout(() => {
      convertDate(calendar, isoDate, ctrl.signal)
        .then((d) => {
          setDual(d);
          setErrors((e) => ({ ...e, date: undefined }));
        })
        .catch((e) => {
          if (e instanceof ApiError) setErrors((er) => ({ ...er, date: e.message }));
        });
    }, 250);
    return () => {
      clearTimeout(t);
      ctrl.abort();
    };
  }, [isoDate, calendar]);

  useEffect(() => {
    if (placeMode !== "search" || place?.label === query) return;
    setPlace(null);
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    const t = setTimeout(() => {
      searchAbort.current?.abort();
      const ctrl = new AbortController();
      searchAbort.current = ctrl;
      searchPlaces(query.trim(), ctrl.signal)
        .then((r) => {
          setResults(r);
          setShowResults(true);
          setActiveIdx(-1);
        })
        .catch(() => undefined);
    }, 200);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, placeMode]);

  useEffect(() => {
    setCoordPlace(null);
    const la = parseFloat(lat);
    const lo = parseFloat(lon);
    if (Number.isNaN(la) || Number.isNaN(lo)) return;
    const t = setTimeout(() => {
      placeFromCoordinates(la, lo)
        .then((p) => {
          setCoordPlace(p);
          setErrors((e) => ({ ...e, place: undefined }));
        })
        .catch((e) => e instanceof ApiError && setErrors((er) => ({ ...er, place: e.message })));
    }, 300);
    return () => clearTimeout(t);
  }, [lat, lon]);

  useEffect(() => {
    if (serverError?.field && ["date", "time", "place"].includes(serverError.field)) {
      setErrors((e) => ({ ...e, [serverError.field as string]: serverError.message }));
    } else if (serverError) {
      setErrors((e) => ({ ...e, form: serverError.message }));
    }
  }, [serverError]);

  const dayOptions = useMemo(() => Array.from({ length: calendar === "BS" ? 32 : 31 }, (_, i) => i + 1), [calendar]);
  const months = calendar === "BS" ? BS_MONTHS : AD_MONTHS;

  function choose(p: Place) {
    setPlace(p);
    setQuery(p.label);
    setShowResults(false);
    setErrors((e) => ({ ...e, place: undefined }));
  }

  function validate(): Errors {
    const e: Errors = {};
    const y = Number(year);
    if (!year || !month || !day) e.date = "Please enter the complete birth date.";
    else if (calendar === "AD" && (y < 1800 || y > 2399)) e.date = "AD years between 1800 and 2399 are supported.";
    else if (calendar === "BS" && (y < 1975 || y > 2100)) e.date = "BS years between 1975 and 2100 are supported.";
    if (unknownTime) e.time = "An exact birth time is required for an accurate Lagna and house calculation.";
    else {
      const h = Number(hour);
      const m = Number(minute);
      const s = second ? Number(second) : 0;
      if (hour === "" || minute === "") e.time = "Please enter the birth time (hour and minute).";
      else if (timeFormat === "12" && (h < 1 || h > 12)) e.time = "With AM/PM the hour must be between 1 and 12.";
      else if (timeFormat === "24" && (h < 0 || h > 23)) e.time = "Hour must be between 0 and 23.";
      else if (m < 0 || m > 59 || s < 0 || s > 59) e.time = "Minutes and seconds must be between 0 and 59.";
    }
    if (placeMode === "search" && !place) e.place = "Please select a specific city or location.";
    if (placeMode === "coords" && !coordPlace) e.place = errors.place || "Please enter valid latitude and longitude.";
    if (offsetOverride && Number.isNaN(Number(offsetOverride))) e.place = "UTC offset must be a number of hours, e.g. 5.75.";
    return e;
  }

  function submit(ev: React.FormEvent) {
    ev.preventDefault();
    const e = validate();
    setErrors(e);
    if (Object.values(e).some(Boolean)) return;
    const time = `${pad(hour)}:${pad(minute)}${second ? ":" + pad(second) : ""}`;
    const req: KundaliRequest = {
      name: name.trim() || undefined,
      calendar,
      date: isoDate,
      time,
      meridiem: timeFormat === "12" ? meridiem : undefined,
      timeAccuracy: accuracy,
    };
    if (placeMode === "search" && place) req.placeId = place.id;
    if (placeMode === "coords" && coordPlace) {
      req.latitude = coordPlace.latitude;
      req.longitude = coordPlace.longitude;
    }
    if (offsetOverride) req.utcOffsetOverride = Number(offsetOverride);
    onSubmit(req);
  }

  return (
    <form className="birth-form" onSubmit={submit} noValidate>
      <div className="field">
        <label htmlFor="name">Name <span className="optional">(optional, used only on the report)</span></label>
        <input id="name" value={name} maxLength={80} onChange={(e) => setName(e.target.value)} autoComplete="off" />
      </div>

      <fieldset className={`field ${errors.date ? "has-error" : ""}`}>
        <legend>Birth date</legend>
        <div className="segmented" role="radiogroup" aria-label="Calendar">
          {(["AD", "BS"] as const).map((c) => (
            <button type="button" key={c} role="radio" aria-checked={calendar === c}
              className={calendar === c ? "active" : ""}
              onClick={() => { setCalendar(c); setMonth(""); setDay(""); setYear(""); }}>
              {c === "AD" ? "AD (Gregorian)" : "BS (Bikram Sambat)"}
            </button>
          ))}
        </div>
        <div className="row three">
          <div>
            <label htmlFor="year" className="sub">Year</label>
            <input id="year" inputMode="numeric" placeholder={calendar === "BS" ? "2057" : "2000"} value={year}
              maxLength={4} onChange={(e) => setYear(e.target.value.replace(/\D/g, ""))} />
          </div>
          <div>
            <label htmlFor="month" className="sub">Month</label>
            <select id="month" value={month} onChange={(e) => setMonth(e.target.value)}>
              <option value="">Month</option>
              {months.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="day" className="sub">Day</label>
            <select id="day" value={day} onChange={(e) => setDay(e.target.value)}>
              <option value="">Day</option>
              {dayOptions.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
        </div>
        {dual && (
          <p className="date-confirm" aria-live="polite">
            <strong>Interpreted as:</strong> {dual.bsLabel ? <>{dual.bsLabel} <span className="dev">({dual.bsLabelDevanagari})</span> · </> : null}
            {dual.adLabel}
            {!dual.bsAvailable && <span className="muted"> (outside the BS table range)</span>}
          </p>
        )}
        {errors.date && <p className="error" role="alert">{errors.date}</p>}
      </fieldset>

      <fieldset className={`field ${errors.time ? "has-error" : ""}`}>
        <legend>Birth time</legend>
        <div className="segmented small" role="radiogroup" aria-label="Time format">
          {(["12", "24"] as const).map((f) => (
            <button type="button" key={f} role="radio" aria-checked={timeFormat === f}
              className={timeFormat === f ? "active" : ""} onClick={() => setTimeFormat(f)}>
              {f === "12" ? "12-hour" : "24-hour"}
            </button>
          ))}
        </div>
        <div className={`row ${timeFormat === "12" ? "four" : "three"}`}>
          <div>
            <label htmlFor="hour" className="sub">Hour</label>
            <input id="hour" inputMode="numeric" maxLength={2} placeholder={timeFormat === "12" ? "10" : "22"}
              value={hour} disabled={unknownTime} onChange={(e) => setHour(e.target.value.replace(/\D/g, ""))} />
          </div>
          <div>
            <label htmlFor="minute" className="sub">Minute</label>
            <input id="minute" inputMode="numeric" maxLength={2} placeholder="30" value={minute} disabled={unknownTime}
              onChange={(e) => setMinute(e.target.value.replace(/\D/g, ""))} />
          </div>
          <div>
            <label htmlFor="second" className="sub">Second <span className="optional">(opt.)</span></label>
            <input id="second" inputMode="numeric" maxLength={2} placeholder="00" value={second} disabled={unknownTime}
              onChange={(e) => setSecond(e.target.value.replace(/\D/g, ""))} />
          </div>
          {timeFormat === "12" && (
            <div>
              <span className="sub">AM / PM</span>
              <div className="segmented small fill" role="radiogroup" aria-label="AM or PM">
                {(["AM", "PM"] as const).map((m) => (
                  <button type="button" key={m} role="radio" aria-checked={meridiem === m} disabled={unknownTime}
                    className={meridiem === m ? "active" : ""} onClick={() => setMeridiem(m)}>{m}</button>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className="row inline-options">
          <label className="radio"><input type="radio" name="acc" checked={accuracy === "exact"}
            onChange={() => setAccuracy("exact")} disabled={unknownTime} /> Exact</label>
          <label className="radio"><input type="radio" name="acc" checked={accuracy === "approximate"}
            onChange={() => setAccuracy("approximate")} disabled={unknownTime} /> Approximate</label>
          <label className="checkbox"><input type="checkbox" checked={unknownTime}
            onChange={(e) => setUnknownTime(e.target.checked)} /> I don't know my birth time</label>
        </div>
        {unknownTime && (
          <p className="notice">An exact birth time is required for an accurate Lagna and house calculation. Please
            find the recorded time (for example from the family's handwritten china) before generating a full Kundali.</p>
        )}
        {errors.time && !unknownTime && <p className="error" role="alert">{errors.time}</p>}
      </fieldset>

      <fieldset className={`field ${errors.place ? "has-error" : ""}`}>
        <legend>Birthplace</legend>
        <div className="segmented small" role="radiogroup" aria-label="Place input">
          <button type="button" role="radio" aria-checked={placeMode === "search"}
            className={placeMode === "search" ? "active" : ""} onClick={() => setPlaceMode("search")}>Search city</button>
          <button type="button" role="radio" aria-checked={placeMode === "coords"}
            className={placeMode === "coords" ? "active" : ""} onClick={() => setPlaceMode("coords")}>Enter coordinates</button>
        </div>
        {placeMode === "search" ? (
          <div className="combo">
            <input aria-label="Search birthplace" placeholder="e.g. Kathmandu, Pokhara, New York" value={query}
              role="combobox" aria-expanded={showResults} aria-controls="place-list" aria-autocomplete="list"
              onChange={(e) => setQuery(e.target.value)} onFocus={() => results.length && setShowResults(true)}
              onBlur={() => setTimeout(() => setShowResults(false), 150)}
              onKeyDown={(e) => {
                if (!showResults || !results.length) return;
                if (e.key === "ArrowDown") { e.preventDefault(); setActiveIdx((i) => Math.min(i + 1, results.length - 1)); }
                if (e.key === "ArrowUp") { e.preventDefault(); setActiveIdx((i) => Math.max(i - 1, 0)); }
                if (e.key === "Enter" && activeIdx >= 0) { e.preventDefault(); choose(results[activeIdx]); }
                if (e.key === "Escape") setShowResults(false);
              }} autoComplete="off" />
            {showResults && results.length > 0 && (
              <ul className="combo-list" id="place-list" role="listbox">
                {results.map((r, i) => (
                  <li key={r.id} role="option" aria-selected={i === activeIdx}
                    className={i === activeIdx ? "active" : ""} onMouseDown={() => choose(r)}>
                    <span className="combo-main">{r.label}</span>
                    <span className="combo-meta">{fmtLatLon(r.latitude, r.longitude)} · {r.timezone}</span>
                  </li>
                ))}
              </ul>
            )}
            {showResults && query.length >= 2 && results.length === 0 && (
              <p className="muted small">No match. Try a nearby larger town, or enter coordinates.</p>
            )}
            {place && (
              <p className="date-confirm"><strong>Selected:</strong> {place.label} · {fmtLatLon(place.latitude, place.longitude)} · {place.timezone}
                {place.source !== "GeoNames" && <span className="muted"> ({place.source})</span>}</p>
            )}
          </div>
        ) : (
          <>
            <div className="row two">
              <div>
                <label htmlFor="lat" className="sub">Latitude (N +, S −)</label>
                <input id="lat" inputMode="decimal" placeholder="27.7172" value={lat} onChange={(e) => setLat(e.target.value)} />
              </div>
              <div>
                <label htmlFor="lon" className="sub">Longitude (E +, W −)</label>
                <input id="lon" inputMode="decimal" placeholder="85.3240" value={lon} onChange={(e) => setLon(e.target.value)} />
              </div>
            </div>
            {coordPlace && <p className="date-confirm"><strong>Timezone:</strong> {coordPlace.timezone}</p>}
          </>
        )}
        <button type="button" className="link-button" onClick={() => setShowAdvanced((s) => !s)} aria-expanded={showAdvanced}>
          {showAdvanced ? "Hide" : "Show"} timezone override
        </button>
        {showAdvanced && (
          <div className="advanced">
            <label htmlFor="offset" className="sub">UTC offset in hours (only if you know the historical clock time differed)</label>
            <input id="offset" inputMode="decimal" placeholder="e.g. 5.75" value={offsetOverride}
              onChange={(e) => setOffsetOverride(e.target.value)} />
          </div>
        )}
        {errors.place && <p className="error" role="alert">{errors.place}</p>}
      </fieldset>

      {errors.form && <p className="error" role="alert">{errors.form}</p>}
      <button className="primary" type="submit" disabled={loading || unknownTime}>
        {loading ? "Calculating…" : "Generate Janma Kundali"}
      </button>
      <p className="privacy">Your birth details are used only to calculate this chart. Nothing is stored, and no account is needed.</p>
    </form>
  );
}
