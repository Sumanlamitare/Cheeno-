import type { Report } from "../types";
import { Badge } from "./common";

const LEVEL_TONE: Record<string, string> = {
  Advanced: "good", Higher: "good", "Graduate with effort": "neutral", Practical: "mixed",
  Wealthy: "good", Prosperous: "good", Comfortable: "neutral", Modest: "mixed",
  "Very happy": "good", Happy: "good", Mixed: "neutral", "Needs work": "mixed",
  "Top of field": "good", "Senior leadership": "good", "Established professional": "neutral", "Steady rise": "mixed",
  "Well supported": "good", Supported: "neutral", "Patience advised": "mixed",
};

export default function Personal({ report }: { report: Report }) {
  const p = report.interpretation.personal;
  if (!p) return null;
  return (
    <div className="personal">
      <p className="lead-small">{p.intro}</p>
      <div className="pa-list">
        {p.answers.map((a: any) => (
          <article key={a.key} className="pa-card">
            <header className="pa-head">
              <div>
                <span className="eyebrow">{a.title}</span>
                <h3>{a.question}</h3>
              </div>
              <Badge tone={LEVEL_TONE[a.level] ?? "neutral"}>{a.level}</Badge>
            </header>
            <p className="pa-answer">{a.answer}</p>
            {a.details?.length > 0 && (
              <>
                <p className="ex-sub">{a.detailTitle}</p>
                <ul className="ex-advice">{a.details.map((d: string, i: number) => <li key={i}>{d}</li>)}</ul>
              </>
            )}
            {a.secondary?.length > 0 && (
              <>
                <p className="ex-sub">{a.secondaryTitle}</p>
                <ul className="ex-advice">{a.secondary.map((d: string, i: number) => <li key={i}>{d}</li>)}</ul>
              </>
            )}
            {a.notes?.map((n: string, i: number) => <p key={i} className="small">{n}</p>)}
            <details className="why">
              <summary>Why this answer (score {a.score})</summary>
              <ul className="pa-factors">
                {a.factors.map((f: any, i: number) => (
                  <li key={i} className={f.points > 0 ? "plus" : "minus"}>
                    <span className="pts">{f.points > 0 ? `+${f.points}` : f.points}</span> {f.why}
                  </li>
                ))}
                {a.factors.length === 0 && <li>No strong factors either way.</li>}
              </ul>
              <p className="small muted">{a.basis}</p>
            </details>
            {a.disclaimer && <p className="small muted">{a.disclaimer}</p>}
          </article>
        ))}
      </div>
      <p className="small muted">{p.method}</p>
    </div>
  );
}
