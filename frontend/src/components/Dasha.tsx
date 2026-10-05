import { Fragment, useMemo, useState } from "react";
import { fmtDate, fmtYears } from "../format";
import type { DashaPeriod, Report } from "../types";
import { Badge } from "./common";

const PLANET_COLOR: Record<string, string> = {
  Sun: "#c8873a", Moon: "#9aa7b0", Mars: "#a8443a", Mercury: "#5f8a5a", Jupiter: "#c9a646",
  Venus: "#c79aa5", Saturn: "#4f5a6b", Rahu: "#6d5a7a", Ketu: "#8a6f58",
};

function statusBadge(s: string) {
  return <Badge tone={s === "current" ? "gold" : s === "past" ? "muted" : "neutral"}>{s}</Badge>;
}

function SubList({ periods, depth }: { periods: DashaPeriod[]; depth: number }) {
  const [open, setOpen] = useState<number | null>(null);
  return (
    <ul className={`dasha-sub depth-${depth}`}>
      {periods.map((p, i) => (
        <li key={i} className={p.status}>
          <div className="dasha-sub-row">
            <span className="dot" style={{ background: PLANET_COLOR[p.lord] }} />
            <strong>{p.lord}</strong>
            <span>{fmtDate(p.start)} → {fmtDate(p.end)}</span>
            <span className="muted">{fmtYears(p.durationYears)}</span>
            {p.status === "current" && statusBadge(p.status)}
            {p.children && (
              <button type="button" className="expand small" aria-expanded={open === i}
                onClick={() => setOpen(open === i ? null : i)}>
                {open === i ? "Hide" : "Pratyantar"}
              </button>
            )}
          </div>
          {open === i && p.children && <SubList periods={p.children} depth={depth + 1} />}
        </li>
      ))}
    </ul>
  );
}

export function DashaTable({ report }: { report: Report }) {
  const periods: DashaPeriod[] = report.dasha.periods;
  const [open, setOpen] = useState<number | null>(periods.findIndex((p) => p.status === "current"));
  const b = report.dasha.balanceAtBirth;
  return (
    <div>
      <p className="lead-small">
        Birth nakshatra lord: <strong>{report.dasha.startingLord}</strong>. Balance of {report.dasha.startingLord} Mahadasha at
        birth: <strong>{b.years}y {b.months}m {b.days}d</strong>.
      </p>
      <table className="data-table responsive">
        <thead><tr><th>Mahadasha</th><th>Start</th><th>End</th><th>Duration</th><th>Status</th><th aria-label="Expand" /></tr></thead>
        <tbody>
          {periods.map((p, i) => (
            <Fragment key={i}>
              <tr className={p.status}>
                <td data-label="Mahadasha"><span className="dot" style={{ background: PLANET_COLOR[p.lord] }} /> <strong>{p.lord}</strong></td>
                <td data-label="Start">{fmtDate(p.start)}{p.beforeBirth && <span className="muted small"> (before birth)</span>}</td>
                <td data-label="End">{fmtDate(p.end)}</td>
                <td data-label="Duration">{fmtYears(p.durationYears)}</td>
                <td data-label="Status">{statusBadge(p.status)}</td>
                <td className="expand-cell">
                  <button type="button" className="expand" aria-expanded={open === i} onClick={() => setOpen(open === i ? null : i)}>
                    {open === i ? "Hide" : "Antardasha"}
                  </button>
                </td>
              </tr>
              {open === i && p.children && (
                <tr className="detail-row"><td colSpan={6}><SubList periods={p.children} depth={1} /></td></tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
      <p className="small muted">Dates are calculated from the Moon's longitude using a {report.dasha.yearDays}-day year. Shown in UTC.</p>
    </div>
  );
}

export function LifeTimeline({ report }: { report: Report }) {
  const periods: DashaPeriod[] = report.dasha.periods;
  const birth = new Date(report.birth.utc);
  const now = new Date(report.meta.generatedAt);
  const start = birth.getTime();
  const lastEnd = new Date(periods[periods.length - 1].end).getTime();
  const end = Math.min(lastEnd, start + 100 * 365.25 * 864e5);
  const span = end - start;
  const pct = (t: number) => Math.max(0, Math.min(100, ((t - start) / span) * 100));
  const birthYear = birth.getUTCFullYear();
  const [year, setYear] = useState<number>(now.getUTCFullYear());

  const selected = useMemo(() => {
    const ys = Date.UTC(year, 0, 1);
    const ye = Date.UTC(year + 1, 0, 1);
    const out: { md: DashaPeriod; ads: { ad: DashaPeriod; pds: DashaPeriod[] }[] }[] = [];
    for (const md of periods) {
      if (new Date(md.end).getTime() <= ys || new Date(md.start).getTime() >= ye) continue;
      const ads = (md.children || []).filter((ad) => new Date(ad.end).getTime() > ys && new Date(ad.start).getTime() < ye)
        .map((ad) => ({ ad, pds: (ad.children || []).filter((pd) => new Date(pd.end).getTime() > ys && new Date(pd.start).getTime() < ye) }));
      out.push({ md, ads });
    }
    return out;
  }, [year, periods]);

  const ticks = [];
  for (let y = Math.ceil(birthYear / 10) * 10; Date.UTC(y, 0, 1) < end; y += 10) ticks.push(y);

  return (
    <div className="timeline">
      <div className="timeline-bar" role="img" aria-label="Mahadasha timeline from birth">
        {periods.map((p, i) => {
          const s = pct(new Date(p.start).getTime());
          const e = pct(new Date(p.end).getTime());
          if (e <= 0 || s >= 100) return null;
          return (
            <div key={i} className={`tl-seg ${p.status}`} style={{ left: `${s}%`, width: `${e - s}%`, background: PLANET_COLOR[p.lord] }}
              title={`${p.lord} Mahadasha: ${fmtDate(p.start)} – ${fmtDate(p.end)}`}>
              {e - s > 6 && <span>{p.lord}</span>}
            </div>
          );
        })}
        <div className="tl-now" style={{ left: `${pct(now.getTime())}%` }} title={`Today: ${fmtDate(now.toISOString())}`}><span>Now</span></div>
      </div>
      <div className="timeline-ticks">
        <span style={{ left: 0 }}>Birth {birthYear}</span>
        {ticks.map((t) => <span key={t} style={{ left: `${pct(Date.UTC(t, 0, 1))}%` }}>{t}</span>)}
      </div>
      <div className="year-picker">
        <label htmlFor="yr">Select a year</label>
        <div className="year-controls">
          <button type="button" onClick={() => setYear((y) => Math.max(birthYear, y - 1))} aria-label="Previous year">‹</button>
          <input id="yr" type="number" min={birthYear} max={birthYear + 100} value={year}
            onChange={(e) => setYear(Math.max(birthYear, Math.min(birthYear + 100, Number(e.target.value) || birthYear)))} />
          <button type="button" onClick={() => setYear((y) => Math.min(birthYear + 100, y + 1))} aria-label="Next year">›</button>
          <span className="muted small">Age {Math.max(0, year - birthYear)}</span>
        </div>
      </div>
      <div className="year-result" aria-live="polite">
        {selected.map(({ md, ads }, i) => (
          <div key={i} className="year-md">
            <h4><span className="dot" style={{ background: PLANET_COLOR[md.lord] }} /> {md.lord} Mahadasha
              <span className="muted small"> {fmtDate(md.start)} → {fmtDate(md.end)}</span></h4>
            <ul>
              {ads.map(({ ad, pds }, j) => (
                <li key={j}>
                  <strong>{md.lord}–{ad.lord}</strong> <span className="muted small">{fmtDate(ad.start)} → {fmtDate(ad.end)}</span>
                  <div className="pd-chips">
                    {pds.map((pd, k) => (
                      <span key={k} className="chip" title={`${fmtDate(pd.start)} → ${fmtDate(pd.end)}`}>
                        {pd.lord} <small>{fmtDate(pd.start).replace(/ \d{4}$/, "")}</small>
                      </span>
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
