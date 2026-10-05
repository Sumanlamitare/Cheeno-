import type { ReactNode } from "react";
import { fmtDate } from "../format";
import type { Group, Item, Reading, TimingWindow } from "../types";

export function Section({ id, num, title, kicker, children }: {
  id: string; num?: number | string; title: string; kicker?: string; children: ReactNode;
}) {
  return (
    <section id={id} className="report-section" aria-labelledby={`${id}-h`}>
      <header className="section-head">
        {num !== undefined && <span className="section-num">{num}</span>}
        <div>
          <h2 id={`${id}-h`}>{title}</h2>
          {kicker && <p className="kicker">{kicker}</p>}
        </div>
      </header>
      {children}
    </section>
  );
}

export function Why({ reasons, label = "Why?", extra }: { reasons: string[]; label?: string; extra?: ReactNode }) {
  if (!reasons?.length && !extra) return null;
  return (
    <details className="why">
      <summary>{label}</summary>
      <ul>
        {reasons.map((r, i) => <li key={i}>{r}</li>)}
      </ul>
      {extra}
    </details>
  );
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: string }) {
  return <span className={`badge tone-${tone}`}>{children}</span>;
}

const polarityTone: Record<string, string> = { positive: "good", negative: "warn", mixed: "mixed", neutral: "neutral" };

export function ItemList({ items }: { items: Item[] }) {
  return (
    <ul className="item-list">
      {items.map((it, i) => (
        <li key={i} className={`item pol-${it.polarity ?? "neutral"}`}>
          <p>{it.text}</p>
          <Why reasons={it.why} />
        </li>
      ))}
    </ul>
  );
}

function GroupCard({ g }: { g: Group }) {
  return (
    <li className={`group pol-${g.polarity}`}>
      <div className="group-head">
        <h4>{g.label}</h4>
        <Badge tone={polarityTone[g.polarity]}>{g.strength}</Badge>
      </div>
      <p>{g.text}</p>
      {g.supporting.length > 0 && (
        <ul className="supporting">
          {g.supporting.map((s, i) => <li key={i}>{s}</li>)}
        </ul>
      )}
      <Why reasons={g.why} extra={
        <p className="why-meta">
          {g.modifiers.length > 0 && <>{g.modifiers.join("; ")}. </>}
          Rules: {g.ruleIds.join(", ")}
        </p>
      } />
    </li>
  );
}

export function ReadingView({ r, hideOverall = false }: { r: Reading; hideOverall?: boolean }) {
  return (
    <div className="reading">
      {!hideOverall && (
        <div className="overall">
          <div className="overall-head">
            <span className="eyebrow">Overall traditional interpretation</span>
            <Badge tone="gold">{r.emphasis}</Badge>
          </div>
          <p>{r.overall}</p>
          {r.balance !== null && (
            <div className="balance" aria-label={`Supportive weight ${Math.round((r.balance ?? 0) * 100)} of 100`}>
              <div className="balance-bar"><span style={{ width: `${(r.balance ?? 0) * 100}%` }} /></div>
              <div className="balance-legend"><span>Supportive</span><span>Challenging</span></div>
            </div>
          )}
          <Why reasons={r.overallWhy} />
        </div>
      )}
      <div className="sc-grid">
        <div>
          <h3 className="col-title good">Strengths</h3>
          {r.strengths.length ? <ul className="groups">{r.strengths.map((g) => <GroupCard key={g.theme + g.polarity} g={g} />)}</ul>
            : <p className="muted">No specific supportive rules were triggered.</p>}
        </div>
        <div>
          <h3 className="col-title warn">Challenges</h3>
          {r.challenges.length ? <ul className="groups">{r.challenges.map((g) => <GroupCard key={g.theme + g.polarity} g={g} />)}</ul>
            : <p className="muted">No specific challenging rules were triggered.</p>}
        </div>
      </div>
      {r.notes.length > 0 && (
        <>
          <h3 className="col-title">Mixed and contextual factors</h3>
          <ul className="groups">{r.notes.map((g) => <GroupCard key={g.theme + g.polarity} g={g} />)}</ul>
        </>
      )}
      {r.keyFactors && <KeyFactors rows={r.keyFactors} />}
      {r.timing && <Timing windows={r.timing.windows} method={r.timing.method} />}
      {r.disclaimer && <p className="disclaimer-inline">{r.disclaimer}</p>}
    </div>
  );
}

export function KeyFactors({ rows }: { rows: { label: string; value: string }[] }) {
  return (
    <div className="key-factors">
      <h3 className="col-title">Chart factors used</h3>
      <dl>
        {rows.map((r) => (
          <div key={r.label}><dt>{r.label}</dt><dd>{r.value}</dd></div>
        ))}
      </dl>
    </div>
  );
}

export function Timing({ windows, method }: { windows: TimingWindow[]; method: string }) {
  return (
    <div className="timing">
      <h3 className="col-title">Traditional timing periods</h3>
      {windows.length === 0 ? <p className="muted">No significator periods fall in the range considered.</p> : (
        <ul className="timing-list">
          {windows.map((w, i) => (
            <li key={i} className={`timing-item ${w.level}`}>
              <div className="timing-head">
                <strong>{w.mahadasha} – {w.antardasha}</strong>
                <span>{fmtDate(w.start)} → {fmtDate(w.end)}</span>
                <Badge tone={w.level === "primary" ? "gold" : "neutral"}>{w.level}</Badge>
              </div>
              <Why reasons={w.why} />
            </li>
          ))}
        </ul>
      )}
      <p className="method">{method}</p>
    </div>
  );
}
