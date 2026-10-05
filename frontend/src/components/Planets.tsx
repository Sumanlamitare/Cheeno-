import { Fragment, useState } from "react";
import { cap, ordinal } from "../format";
import type { PlanetPos, Report } from "../types";
import { Badge, ItemList } from "./common";

function dignityTone(d: string) {
  if (["exalted", "moolatrikona", "own"].includes(d)) return "good";
  if (["debilitated", "great enemy"].includes(d)) return "warn";
  return "neutral";
}

function Detail({ report, p }: { report: Report; p: PlanetPos }) {
  const d = report.interpretation.planets[p.name];
  return (
    <div className="planet-detail">
      <p className="karaka"><strong>{p.name}</strong> ({p.sanskrit}) signifies {d.karaka}.</p>
      <ItemList items={d.items} />
      <dl className="mini-dl">
        <div><dt>Aspects (drishti) on</dt><dd>{d.aspectsHouses.map((h: string) => `${h} house`).join(", ")}</dd></div>
        <div><dt>Nakshatra</dt><dd>{d.nakshatraNote}</dd></div>
        <div><dt>Navamsa (D9)</dt><dd>{d.navamsa.sign} ({d.navamsa.dignity})</dd></div>
        {d.shadbala && (
          <div><dt>Shadbala</dt><dd>{d.shadbala.rupas} rupas (required {d.shadbala.requiredRupas}; ratio {d.shadbala.ratio})</dd></div>
        )}
        <div><dt>Longitude</dt><dd>{p.longitude.toFixed(4)}° sidereal · speed {p.speed.toFixed(4)}°/day</dd></div>
      </dl>
      {d.relationships.length > 0 && (
        <details className="why">
          <summary>Relationships with other grahas</summary>
          <ul>
            {d.relationships.map((r: { planet: string; natural: string; compound: string }) => (
              <li key={r.planet}>{r.planet}: natural {r.natural}, compound (Panchadha) {r.compound}</li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}

export default function PlanetTable({ report }: { report: Report }) {
  const [open, setOpen] = useState<string | null>(null);
  const planets: PlanetPos[] = report.chart.planets;
  const asc = report.chart.ascendant;
  return (
    <div className="planet-table">
      <table className="data-table responsive">
        <thead>
          <tr>
            <th>Planet</th><th>Rashi</th><th>Degree</th><th>House</th><th>Nakshatra</th><th>Pada</th>
            <th>Motion</th><th>Dignity</th><th aria-label="Details" />
          </tr>
        </thead>
        <tbody>
          <tr className="asc-row">
            <td data-label="Planet"><strong>Lagna</strong> <span className="muted">Ascendant</span></td>
            <td data-label="Rashi">{asc.signName}</td>
            <td data-label="Degree">{asc.degreeLabel}</td>
            <td data-label="House">1st</td>
            <td data-label="Nakshatra">{asc.nakshatraName}</td>
            <td data-label="Pada">{asc.pada}</td>
            <td data-label="Motion">—</td>
            <td data-label="Dignity">—</td>
            <td />
          </tr>
          {planets.map((p) => (
            <Fragment key={p.name}>
              <tr className={open === p.name ? "open" : ""}>
                <td data-label="Planet"><strong>{p.name}</strong> <span className="muted">{p.sanskrit}</span></td>
                <td data-label="Rashi">{p.signName}</td>
                <td data-label="Degree">{p.degreeLabel}</td>
                <td data-label="House">{ordinal(p.house)}</td>
                <td data-label="Nakshatra">{p.nakshatraName}</td>
                <td data-label="Pada">{p.pada}</td>
                <td data-label="Motion">
                  {p.motion}{p.combust && <> · <span className="warn-text">Combust</span></>}
                </td>
                <td data-label="Dignity">{p.name === "Rahu" || p.name === "Ketu" ? <span className="muted">{p.dignity}</span>
                  : <Badge tone={dignityTone(p.dignity)}>{cap(p.dignity)}</Badge>}</td>
                <td className="expand-cell">
                  <button type="button" className="expand" aria-expanded={open === p.name}
                    onClick={() => setOpen(open === p.name ? null : p.name)}>
                    {open === p.name ? "Close" : "Explain"}
                  </button>
                </td>
              </tr>
              {open === p.name && (
                <tr className="detail-row"><td colSpan={9}><Detail report={report} p={p} /></td></tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ShadbalaTable({ report }: { report: Report }) {
  const sb = report.shadbala;
  if (!sb) return <p className="muted">Shadbala could not be calculated because sunrise is undefined at this latitude.</p>;
  const rows = Object.entries(sb.planets) as [string, any][];
  const max = Math.max(...rows.map(([, v]) => v.ratio), 1.6);
  return (
    <div className="shadbala">
      <table className="data-table responsive compact">
        <thead>
          <tr><th>Planet</th><th>Sthana</th><th>Dig</th><th>Kala</th><th>Chesta</th><th>Naisargika</th><th>Drik</th>
            <th>Total (rupas)</th><th>Required</th><th>Strength</th></tr>
        </thead>
        <tbody>
          {rows.map(([p, v]) => (
            <tr key={p}>
              <td data-label="Planet"><strong>{p}</strong></td>
              <td data-label="Sthana">{v.components.sthana.total}</td>
              <td data-label="Dig">{v.components.dig}</td>
              <td data-label="Kala">{v.components.kala.total}</td>
              <td data-label="Chesta">{v.components.chesta}</td>
              <td data-label="Naisargika">{v.components.naisargika}</td>
              <td data-label="Drik">{v.components.drik}</td>
              <td data-label="Total"><strong>{v.rupas}</strong></td>
              <td data-label="Required">{v.requiredRupas}</td>
              <td data-label="Strength">
                <div className="meter" title={`${v.ratio}× required`}>
                  <span className={v.sufficient ? "ok" : "low"} style={{ width: `${Math.min(v.ratio / max, 1) * 100}%` }} />
                  <i style={{ left: `${(1 / max) * 100}%` }} />
                </div>
                <span className="small">{v.ratio}×</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="small muted">Components in virupas (60 virupas = 1 rupa). The marker on each bar is the classical minimum.</p>
      <details className="why">
        <summary>Shadbala methodology</summary>
        <ul>{sb.methodNotes.map((n: string, i: number) => <li key={i}>{n}</li>)}</ul>
        <p className="why-meta">Time lords used: Vara {sb.inputs.varaLord}, Hora {sb.inputs.horaLord}, Abda {sb.inputs.abdaLord},
          Masa {sb.inputs.masaLord}, Tribhaga {sb.inputs.tribhagaLord}.
          {sb.planetaryWar.length > 0 && ` Planetary war: ${sb.planetaryWar.map((w: any) => `${w.winner} over ${w.loser}`).join(", ")}.`}</p>
      </details>
    </div>
  );
}
