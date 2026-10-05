import { fmtDate, ordinal } from "../format";
import type { Report } from "../types";
import { Badge, ItemList, Why } from "./common";

export function Gochar({ report }: { report: Report }) {
  const items = report.interpretation.gochar;
  const major = items.filter((i: any) => i.major);
  const minor = items.filter((i: any) => !i.major);
  const ing = report.gochar.upcomingIngresses;
  const tone = (r: string) => (r === "favourable" ? "good" : r === "obstructed" ? "mixed" : "warn");
  const Card = ({ it }: { it: any }) => (
    <li className={`transit-card res-${it.result}`}>
      <div className="transit-flow">
        <div><span className="eyebrow">Current transit</span><strong>{it.planet}</strong>
          <span className="muted small">{it.why[0].replace(`${it.planet} transits `, "")}</span></div>
        <span className="arrow" aria-hidden>→</span>
        <div><span className="eyebrow">Natal house affected</span><strong>{ordinal(it.houseFromLagna)} from Lagna</strong>
          <span className="muted small">{ordinal(it.houseFromMoon)} from Moon</span></div>
        <Badge tone={tone(it.result)}>{it.result}</Badge>
      </div>
      <p>{it.text}</p>
      {it.notes.map((n: string, i: number) => <p key={i} className="small">{n}</p>)}
      <Why reasons={[...it.why, `The ${ordinal(it.houseFromLagna)} house signifies: ${it.natalHouseTopic.toLowerCase()}`]} />
    </li>
  );
  return (
    <div>
      <p className="lead-small">Positions calculated for {fmtDate(report.gochar.asOf)}. Results are counted from the natal Moon
        (Chandra Lagna), as is traditional for Gochar, with Vedha (obstruction) applied.</p>
      <h3 className="col-title">Major transits</h3>
      <ul className="transit-list">{major.map((it: any) => <Card key={it.planet} it={it} />)}</ul>
      <details className="why">
        <summary>Faster-moving planets</summary>
        <ul className="transit-list">{minor.map((it: any) => <Card key={it.planet} it={it} />)}</ul>
      </details>
      {ing.length > 0 && (
        <>
          <h3 className="col-title">Upcoming sign changes</h3>
          <table className="data-table responsive compact">
            <thead><tr><th>Date</th><th>Planet</th><th>Enters</th><th>From Moon</th><th>From Lagna</th></tr></thead>
            <tbody>
              {ing.map((e: any, i: number) => (
                <tr key={i}><td data-label="Date">{fmtDate(e.date)}</td><td data-label="Planet">{e.planet}</td>
                  <td data-label="Enters">{e.toSignName}</td><td data-label="From Moon">{ordinal(e.houseFromMoon)}</td>
                  <td data-label="From Lagna">{ordinal(e.houseFromLagna)}</td></tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}

export function SadeSati({ report }: { report: Report }) {
  const ss = report.sadesati;
  const items = report.interpretation.sadesati.items;
  const cur = ss.currentCycle;
  const next = ss.cycles.find((c: any) => c.status === "upcoming");
  return (
    <div>
      <div className="status-row">
        <div className="stat"><span className="eyebrow">Status</span><strong>{ss.status}</strong></div>
        <div className="stat"><span className="eyebrow">Natal Moon</span><strong>{ss.moonSign}</strong></div>
        <div className="stat"><span className="eyebrow">Saturn now</span><strong>{ss.saturnSignNow}</strong></div>
        {cur && <div className="stat"><span className="eyebrow">Current cycle</span><strong>{fmtDate(cur.start)} – {fmtDate(cur.end)}</strong></div>}
        {!cur && next && <div className="stat"><span className="eyebrow">Next begins</span><strong>{fmtDate(next.start)}</strong></div>}
      </div>
      <ItemList items={items.map((i: any) => ({ ...i, polarity: "neutral" }))} />
      <h3 className="col-title">Sade Sati periods in this lifetime</h3>
      <ul className="cycles">
        {ss.cycles.map((c: any, i: number) => (
          <li key={i} className={c.status}>
            <div className="cycle-head">
              <strong>{fmtDate(c.start)} – {fmtDate(c.end)}</strong>
              <Badge tone={c.status === "current" ? "gold" : c.status === "past" ? "muted" : "neutral"}>{c.status}</Badge>
              {c.startsBeforeRange && <span className="small muted">began before birth</span>}
            </div>
            <ol className="phases">
              {c.phases.map((p: any) => (
                <li key={p.phase} className={p.status}>
                  <span>{p.name}</span><span className="muted small">Saturn in {p.saturnSign}</span>
                  <span>{fmtDate(p.start)} – {fmtDate(p.end)}</span>
                </li>
              ))}
            </ol>
          </li>
        ))}
      </ul>
      {ss.dhaiya.length > 0 && (
        <>
          <h3 className="col-title">Dhaiya (Kantaka / Ashtama Shani)</h3>
          <ul className="simple-list">
            {ss.dhaiya.map((d: any, i: number) => (
              <li key={i}>{d.name}: {fmtDate(d.start)} – {fmtDate(d.end)} <Badge tone={d.status === "current" ? "gold" : "muted"}>{d.status}</Badge></li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
