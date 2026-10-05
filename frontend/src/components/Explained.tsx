import type { Report } from "../types";
import { Badge, Why } from "./common";

const toneFor: Record<string, string> = { strong: "good", steady: "neutral", "needs support": "warn" };

export default function Explained({ report }: { report: Report }) {
  const e = report.explained;
  if (!e) return null;
  return (
    <div className="explained">
      <div className="ex-intro">
        {e.intro.map((p: string, i: number) => <p key={i}>{p}</p>)}
      </div>

      <h3 className="col-title">1 · Who you are</h3>
      <div className="ex-grid">
        {e.core.map((c: any) => (
          <article key={c.title} className="ex-card">
            <h4>{c.title}</h4>
            <p>{c.text}</p>
            <Why reasons={c.why} />
          </article>
        ))}
      </div>

      <h3 className="col-title">2 · Your nine grahas</h3>
      <p className="lead-small">Each graha is a part of life. Its house shows <em>where</em> that energy works, and its sign
        shows <em>how comfortable</em> it is there.</p>
      <div className="ex-grid">
        {e.grahas.map((g: any) => (
          <article key={g.planet} className="ex-card">
            <div className="group-head">
              <h4>{g.planet}</h4>
              <Badge tone={toneFor[g.strength]}>{g.strength}</Badge>
            </div>
            <p className="small muted">{g.headline.split(":")[0]}</p>
            <p>{g.text}</p>
            <Why reasons={g.why} />
          </article>
        ))}
      </div>

      <h3 className="col-title">3 · Your life areas</h3>
      <div className="ex-areas">
        {e.areas.map((a: any) => (
          <article key={a.key} className="ex-area">
            <h4>{a.title}</h4>
            <p className="ex-summary">{a.summary}</p>
            <ul className="ex-points">
              {a.points.map((pt: any, i: number) => (
                <li key={i} className={`pt-${pt.tone}`}>
                  <span className="ex-mark">{pt.tone === "good" ? "Strength" : pt.tone === "watch" ? "Watch" : "Note"}</span>
                  <span>{pt.text}</span>
                  <Why reasons={pt.why} />
                </li>
              ))}
            </ul>
            {a.extra && <p className="small">{a.extra}</p>}
            {a.timing.length > 0 && (
              <p className="small"><strong>Periods traditionally favourable to watch:</strong> {a.timing.join("; ")}.</p>
            )}
            <details className="why"><summary>Houses involved</summary><p className="small">{a.houses}.</p></details>
            {a.disclaimer && <p className="small muted">{a.disclaimer}</p>}
            <a className="small" href={`#${a.key}`}>Full {a.title.toLowerCase()} reading ↓</a>
          </article>
        ))}
      </div>

      {e.period && (
        <>
          <h3 className="col-title">4 · The period you are in now</h3>
          <article className="ex-card wide">
            <p><strong>{e.period.text}</strong></p>
            {e.period.themes.map((t: string, i: number) => <p key={i}>{t}</p>)}
            {e.period.activation.map((t: string, i: number) => <p key={i} className="small">{t}</p>)}
            <p>{e.period.summary}</p>
            <p className="small">{e.period.sadeSati}</p>
          </article>
        </>
      )}

      {(e.yogas.length > 0 || e.doshas.length > 0) && (
        <>
          <h3 className="col-title">5 · Special combinations</h3>
          <div className="ex-grid">
            {e.yogas.map((y: any) => (
              <article key={y.name} className="ex-card">
                <div className="group-head"><h4>{y.name}</h4><Badge tone="good">{y.strength}</Badge></div>
                <p>{y.text}</p>
              </article>
            ))}
            {e.doshas.map((d: any) => (
              <article key={d.name} className="ex-card">
                <div className="group-head"><h4>{d.name}</h4><Badge tone="mixed">{d.status}</Badge></div>
                <p>{d.text}</p>
              </article>
            ))}
          </div>
        </>
      )}

      <p className="ex-closing">{e.closing}</p>

      <details className="glossary">
        <summary>Glossary of Jyotish words</summary>
        <dl>
          {e.glossary.map((g: any) => (
            <div key={g.term}><dt>{g.term}</dt><dd>{g.meaning}</dd></div>
          ))}
        </dl>
      </details>
    </div>
  );
}
