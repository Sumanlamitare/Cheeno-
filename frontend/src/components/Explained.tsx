import type { Report } from "../types";
import { Badge, Why } from "./common";

const toneFor: Record<string, string> = { strong: "good", steady: "neutral", "needs support": "warn" };
const meaningTone: Record<string, string> = { positive: "pt-good", negative: "pt-watch", mixed: "pt-note" };

export default function Explained({ report }: { report: Report }) {
  const e = report.explained;
  if (!e) return null;
  return (
    <div className="explained">
      <div className="ex-glance">
        <span className="eyebrow">{e.forName ? `${e.forName}, your life at a glance` : "Your life at a glance"}</span>
        <ul>{e.glance.map((g: string, i: number) => <li key={i}>{g}</li>)}</ul>
      </div>

      <h3 className="col-title">1 · Who you are</h3>
      <div className="ex-grid">
        {e.core.map((c: any) => (
          <article key={c.title} className="ex-card">
            <h4>{c.title}</h4>
            {c.forYou && <p className="ex-you">{c.forYou}</p>}
            <p>{c.text}</p>
            <Why reasons={c.why} />
          </article>
        ))}
      </div>

      <h3 className="col-title">2 · Your life areas: what they mean for you</h3>
      <div className="ex-areas">
        {e.areas.map((a: any) => (
          <article key={a.key} className="ex-area">
            <h4>{a.title}</h4>
            <p className="ex-summary">{a.verdict}</p>
            <p className="ex-sub">What this means for you</p>
            <ul className="ex-points">
              {a.meaning.map((m: any, i: number) => (
                <li key={i} className={meaningTone[m.tone] ?? "pt-good"}>
                  <span>{m.text}</span>
                  <Why reasons={m.why} />
                </li>
              ))}
            </ul>
            {a.extra && <p className="small">{a.extra}</p>}
            {a.advice.length > 0 && (
              <>
                <p className="ex-sub">What you can do</p>
                <ul className="ex-advice">{a.advice.map((x: string, i: number) => <li key={i}>{x}</li>)}</ul>
              </>
            )}
            {a.timing.length > 0 && (
              <p className="small"><strong>Good periods for this:</strong> {a.timing.join("; ")}.</p>
            )}
            <details className="why">
              <summary>Classical indicators behind this</summary>
              <ul>{a.points.map((pt: any, i: number) => <li key={i}>{pt.text}</li>)}</ul>
              <p className="small">{a.houses}.</p>
            </details>
            {a.disclaimer && <p className="small muted">{a.disclaimer}</p>}
            <a className="small" href={`#${a.key}`}>Full {a.title.toLowerCase()} reading ↓</a>
          </article>
        ))}
      </div>

      {e.period && (
        <>
          <h3 className="col-title">3 · What this time in your life means</h3>
          <article className="ex-card wide">
            <ul className="ex-advice">{e.period.forYou.map((t: string, i: number) => <li key={i}>{t}</li>)}</ul>
            {e.period.upcoming.length > 0 && (
              <>
                <p className="ex-sub">Coming up</p>
                <ul className="ex-advice">{e.period.upcoming.map((t: string, i: number) => <li key={i}>{t}</li>)}</ul>
              </>
            )}
            <p className="small">{e.period.sadeSati}</p>
            <details className="why">
              <summary>Traditional meaning of these periods</summary>
              {e.period.themes.map((t: string, i: number) => <p key={i}>{t}</p>)}
              {e.period.activation.map((t: string, i: number) => <p key={i} className="small">{t}</p>)}
            </details>
          </article>
        </>
      )}

      <h3 className="col-title">4 · Your nine grahas: what each means for you</h3>
      <div className="ex-grid">
        {e.grahas.map((g: any) => (
          <article key={g.planet} className="ex-card">
            <div className="group-head">
              <h4>{g.planet}</h4>
              <Badge tone={toneFor[g.strength]}>{g.strength}</Badge>
            </div>
            <p className="small muted">{g.headline.split(":")[0]}</p>
            <p className="ex-you">{g.forYou}</p>
            <details className="why">
              <summary>Classical reading</summary>
              <p>{g.text}</p>
              <ul>{g.why.map((w: string, i: number) => <li key={i}>{w}</li>)}</ul>
            </details>
          </article>
        ))}
      </div>

      {(e.yogas.length > 0 || e.doshas.length > 0) && (
        <>
          <h3 className="col-title">5 · Special combinations in your chart</h3>
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

      <details className="glossary">
        <summary>What is a Kundali? (and a glossary of Jyotish words)</summary>
        {e.intro.map((p: string, i: number) => <p key={i}>{p}</p>)}
        <dl>
          {e.glossary.map((g: any) => (
            <div key={g.term}><dt>{g.term}</dt><dd>{g.meaning}</dd></div>
          ))}
        </dl>
      </details>

      <p className="ex-closing">{e.closing}</p>
    </div>
  );
}
