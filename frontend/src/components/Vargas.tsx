import { useState } from "react";
import { RASHIS, cap, ordinal } from "../format";
import type { Report } from "../types";
import KundaliChart from "./KundaliChart";
import { ReadingView } from "./common";

const ABBR: Record<string, string> = { Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke" };

export function VargaChart({ report, division, title }: { report: Report; division: number; title?: string }) {
  const v = report.chart.vargas[String(division)];
  const entries = Object.entries(v.planets).map(([name, p]: [string, any]) => ({
    name, abbr: ABBR[name], house: p.house, dignity: p.dignity,
    retrograde: report.chart.planets.find((x: any) => x.name === name)?.retrograde,
  }));
  return <KundaliChart lagnaSign={v.lagna} entries={entries} showDegrees={false}
    title={title ?? `D${division} · ${v.name}`} subtitle={`${v.purpose} · Lagna ${RASHIS[v.lagna]}`} />;
}

function VargaTable({ report, division }: { report: Report; division: number }) {
  const v = report.chart.vargas[String(division)];
  return (
    <table className="data-table responsive compact">
      <thead><tr><th>Planet</th><th>D1 sign</th><th>D{division} sign</th><th>D{division} house</th><th>Dignity</th></tr></thead>
      <tbody>
        {report.chart.planets.map((p: any) => {
          const vp = v.planets[p.name];
          return (
            <tr key={p.name}>
              <td data-label="Planet"><strong>{p.name}</strong>{division === 9 && vp.sign === p.sign && <span className="badge tone-gold">Vargottama</span>}</td>
              <td data-label="D1 sign">{p.signName}</td>
              <td data-label={`D${division} sign`}>{vp.signName}</td>
              <td data-label={`D${division} house`}>{ordinal(vp.house)}</td>
              <td data-label="Dignity">{cap(vp.dignity)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export function VargaSection({ report, division }: { report: Report; division: 9 | 10 }) {
  const r = report.interpretation[division === 9 ? "d9" : "d10"];
  return (
    <div className="varga-section">
      <div className="chart-with-table">
        <VargaChart report={report} division={division} />
        <div>
          <p className="lead-small"><strong>D{division} Lagna:</strong> {r.chart.lagnaName}. {r.note}</p>
          <VargaTable report={report} division={division} />
        </div>
      </div>
      <ReadingView r={r} />
    </div>
  );
}

export function AdvancedVargas({ report }: { report: Report }) {
  const divisions = Object.keys(report.chart.vargas).map(Number).filter((d) => ![1, 9, 10].includes(d));
  const [div, setDiv] = useState(divisions[0]);
  return (
    <details className="advanced-vargas">
      <summary>Advanced: other divisional charts (Shodasavarga)</summary>
      <p className="small muted">All sixteen Parashari vargas are calculated mathematically. They are shown for reference;
        the interpretation above uses D1, D9 and D10 (plus D7 and D24 in the children and education analyses).</p>
      <div className="varga-tabs" role="tablist">
        {divisions.map((d) => (
          <button key={d} type="button" role="tab" aria-selected={div === d} className={div === d ? "active" : ""}
            onClick={() => setDiv(d)}>D{d}</button>
        ))}
      </div>
      <div className="chart-with-table">
        <VargaChart report={report} division={div} />
        <VargaTable report={report} division={div} />
      </div>
    </details>
  );
}
