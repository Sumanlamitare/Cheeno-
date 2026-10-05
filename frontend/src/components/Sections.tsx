import { fmtDate, ordinal } from "../format";
import type { Report } from "../types";
import { Badge, ItemList, ReadingView, Why } from "./common";

export function LagnaSection({ report }: { report: Report }) {
  const l = report.interpretation.lagna;
  const f = l.facts;
  const sp = l.signProfile;
  return (
    <div>
      <dl className="fact-grid">
        <div><dt>Ascendant</dt><dd>{f.lagnaSign} {f.lagnaDegree}</dd></div>
        <div><dt>Lagna nakshatra</dt><dd>{f.lagnaNakshatra} (pada {f.lagnaPada})</dd></div>
        <div><dt>Lagna lord</dt><dd>{f.lagnaLord}</dd></div>
        <div><dt>Lord's house</dt><dd>{ordinal(f.lagnaLordHouse)}</dd></div>
        <div><dt>Lord's sign</dt><dd>{f.lagnaLordSign} ({f.lagnaLordDignity})</dd></div>
        <div><dt>Lord's nakshatra</dt><dd>{f.lagnaLordNakshatra}</dd></div>
      </dl>
      <div className="profile">
        <p><strong>Personality.</strong> {sp.personality}</p>
        <p><strong>Temperament.</strong> {sp.temperament}</p>
        <p><strong>General behaviour.</strong> {sp.behaviour}</p>
        <p><strong>Life orientation.</strong> {sp.orientation}</p>
        <p><strong>Classical strengths.</strong> {sp.strengths} <strong>Classical challenges.</strong> {sp.challenges}</p>
        <p>{l.nakshatraNote.text}</p>
        <p>{l.lordNote.text}</p>
        <Why reasons={[...sp.why, ...l.nakshatraNote.why, ...l.lordNote.why]} />
      </div>
      <p className="lead-small">How the rest of the chart modifies this Lagna:</p>
      <ReadingView r={l} />
    </div>
  );
}

export function MoonSection({ report }: { report: Report }) {
  const m = report.interpretation.moon;
  return (
    <div>
      <dl className="fact-grid">
        <div><dt>Janma Rashi</dt><dd>{m.janmaRashi}</dd></div>
        <div><dt>Moon degree</dt><dd>{m.moonDegree}</dd></div>
        <div><dt>Janma Nakshatra</dt><dd>{m.nakshatra}</dd></div>
        <div><dt>Pada</dt><dd>{m.pada}</dd></div>
        <div><dt>Nakshatra lord</dt><dd>{m.nakshatraLord}</dd></div>
        <div><dt>Gana</dt><dd>{m.gana}</dd></div>
      </dl>
      <div className="nakshatra-card">
        <div className="nk-head">
          <h3>{m.nakshatra}</h3>
          <span className="muted">{m.span.start.toFixed(2)}° – {m.span.end.toFixed(2)}° sidereal · 13°20' span · 4 padas</span>
        </div>
        <dl className="mini-dl">
          <div><dt>Deity</dt><dd>{m.deity}</dd></div>
          <div><dt>Symbol</dt><dd>{m.symbol}</dd></div>
          <div><dt>Nature</dt><dd>{m.nature}</dd></div>
          <div><dt>Ruling planet</dt><dd>{m.nakshatraLord}</dd></div>
        </dl>
        <p>{m.characteristics}</p>
        <p>{m.nakshatraInterpretation}</p>
        <p className="small">{m.ganaText}</p>
      </div>
      <ItemList items={m.items} />
    </div>
  );
}

export function YogasSection({ report }: { report: Report }) {
  const y = report.interpretation.yogas;
  return (
    <div>
      <p className="lead-small">{y.note}</p>
      {y.detected.length === 0 && <p className="muted">None of the yogas checked are formed in this chart.</p>}
      <ul className="yoga-list">
        {y.detected.map((d: any) => (
          <li key={d.key} className={`yoga-card ${d.group === "adverse" ? "adverse" : ""}`}>
            <div className="group-head">
              <h4>{d.name}</h4>
              <Badge tone={d.strength === "Strong" ? "good" : d.strength === "Weak" ? "warn" : "neutral"}>{d.strength}</Badge>
            </div>
            <span className="eyebrow">{d.groupLabel}</span>
            <p>{d.text}</p>
            <Why label="Why? (conditions met)" reasons={d.why} />
          </li>
        ))}
      </ul>
      <details className="why">
        <summary>All yoga rules checked ({y.checked.length})</summary>
        <ul>{y.checked.map((c: any) => <li key={c.id}><strong>{c.name}:</strong> {c.definition}</li>)}</ul>
      </details>
    </div>
  );
}

export function DoshasSection({ report }: { report: Report }) {
  const ds = report.interpretation.doshas;
  return (
    <ul className="dosha-list">
      {ds.map((d: any) => (
        <li key={d.id} className={`dosha-card ${d.detected ? "detected" : ""}`}>
          <div className="group-head">
            <h4>{d.name}</h4>
            <Badge tone={d.detected ? (d.mitigations?.length ? "mixed" : "warn") : "good"}>{d.status}</Badge>
          </div>
          {d.type && <p className="small"><strong>Type:</strong> {d.type}{d.variant ? ` (${d.variant})` : ""}</p>}
          {d.severity && d.detected && <p className="small"><strong>Severity / context:</strong> {d.severity}</p>}
          <p>{d.text}</p>
          {d.mitigations?.length > 0 && (
            <div className="mitigations"><strong>{d.detected ? "Mitigating factors" : "Cancellations"}:</strong>
              <ul>{d.mitigations.map((m: string, i: number) => <li key={i}>{m}</li>)}</ul></div>
          )}
          {d.note && <p className="small muted">{d.note}</p>}
          <Why label="Rule used" reasons={[d.rule, ...(d.placements || [])]} />
          {d.disputed && <p className="small muted">Calculated according to the application's defined traditional rule; this combination is disputed between traditions.</p>}
        </li>
      ))}
    </ul>
  );
}

export function CurrentDasha({ report }: { report: Report }) {
  const cd = report.interpretation.currentDasha;
  const cur = report.dasha.current;
  if (!cd) return <p className="muted">The current period could not be determined.</p>;
  return (
    <div>
      <div className="status-row">
        {cur.map((c: any) => (
          <div key={c.level} className="stat">
            <span className="eyebrow">{c.level}</span><strong>{c.lord}</strong>
            <span className="small muted">{fmtDate(c.start)} – {fmtDate(c.end)}</span>
          </div>
        ))}
      </div>
      {cd.activations.map((a: any) => (
        <div key={a.level} className="activation">
          <h4>{a.planet} {a.level} <Badge tone={a.tone === "supportive" ? "good" : a.tone === "demanding" ? "warn" : "mixed"}>{a.tone}</Badge></h4>
          <p>{a.theme}</p>
          <p>{a.activation}</p>
          <Why reasons={a.why} />
        </div>
      ))}
      <ReadingView r={cd} />
      {cd.transitSupport.length > 0 && (
        <>
          <h3 className="col-title">Supporting and transiting factors</h3>
          <ItemList items={cd.transitSupport} />
        </>
      )}
    </div>
  );
}

export function CareerExtras({ report }: { report: Report }) {
  const t = report.interpretation.career.themes;
  return (
    <div className="career-themes">
      <h3 className="col-title">Traditional career themes</h3>
      <p className="lead-small">Work environments emphasised: {t.workStyles.join("; ")}.</p>
      <div className="theme-cards">
        {t.dominantPlanets.map((d: any) => (
          <div key={d.planet} className="theme-card">
            <h4>{d.planet}</h4>
            <ul>{d.fields.map((f: string) => <li key={f}>{f}</li>)}</ul>
            <Why reasons={d.why.map((w: string) => `${d.planet} ${w}`)} />
          </div>
        ))}
      </div>
      <p className="small muted">{t.note}</p>
    </div>
  );
}

export function HealthExtras({ report }: { report: Report }) {
  const h = report.interpretation.health;
  if (!h.bodyAreas.length) return null;
  return (
    <div>
      <h3 className="col-title">Body regions emphasised in Kalapurusha symbolism</h3>
      <ul className="simple-list">
        {h.bodyAreas.map((b: any) => <li key={b.house}>{b.region} <span className="muted">({b.why})</span></li>)}
      </ul>
    </div>
  );
}

export function PanchangaSection({ report }: { report: Report }) {
  const p = report.panchanga;
  const e = report.interpretation.panchanga;
  const rows = [
    { k: "Tithi", v: `${p.tithi.label} (${p.tithi.number} of 30)`, ex: e.tithi },
    { k: "Vara", v: `${p.vara.name} · ${p.vara.english} (lord ${p.vara.lord})`, ex: e.vara },
    { k: "Nakshatra", v: `${p.nakshatra.name}, pada ${p.nakshatra.pada} (lord ${p.nakshatra.lord})`, ex: e.nakshatra },
    { k: "Yoga", v: p.yoga.name, ex: e.yoga },
    { k: "Karana", v: p.karana.name, ex: e.karana },
  ];
  return (
    <div>
      <div className="panchanga-grid">
        {rows.map((r) => (
          <div key={r.k} className="panchanga-card">
            <span className="eyebrow">{r.k}</span>
            <strong>{r.v}</strong>
            <p>{r.ex}</p>
          </div>
        ))}
      </div>
      <dl className="mini-dl">
        <div><dt>Lunar month</dt><dd>{p.lunarMonth.purnimanta} (Purnimanta, as used in Nepal) · {p.lunarMonth.amanta} (Amanta)</dd></div>
        {p.ishtaKala && <div><dt>Ishta Kala</dt><dd>{p.ishtaKala.label} after sunrise</dd></div>}
        {p.sunriseUtc && <div><dt>Sunrise / sunset</dt><dd>{new Date(p.sunriseUtc).toISOString().slice(11, 16)} / {new Date(p.sunsetUtc).toISOString().slice(11, 16)} UTC</dd></div>}
        <div><dt>Birth during</dt><dd>{p.dayBirth === null ? "—" : p.dayBirth ? "Day (Dinamana)" : "Night (Ratrimana)"}</dd></div>
      </dl>
      <p className="small muted">The Hindu day (Vara) begins at sunrise, so a birth before sunrise belongs to the previous weekday.</p>
    </div>
  );
}

export function CalculationDetails({ report }: { report: Report }) {
  const c = report.calculation;
  const b = report.birth;
  const rows: [string, string][] = [
    ["Zodiac", c.zodiac], ["Ayanamsha", `${c.ayanamsha} (${c.ayanamshaValue})`], ["House method", c.houseSystem],
    ["Ephemeris", c.ephemeris], ["Rahu / Ketu", c.nodes], ["Vimshottari year", c.dashaYear],
    ["Birth location", c.location], ["Latitude", c.latitude.toFixed(4)], ["Longitude", c.longitude.toFixed(4)],
    ["Timezone", c.timezone], ["UTC offset on birth date", c.utcOffset],
    ["Daylight saving", c.dst === null ? "Not applicable (manual)" : c.dst ? "Yes" : "No"],
    ["Timezone method", c.timezoneMethod], ["Birth moment (UTC)", b.utc.replace("T", " ").slice(0, 19)],
    ["Julian Day (UT)", String(b.julianDay)], ["Sunrise convention", c.sunrise],
  ];
  return (
    <details className="calc-details" open>
      <summary>Calculation details</summary>
      <dl className="mini-dl">{rows.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
      <p className="small">{c.accuracyNote}</p>
    </details>
  );
}
