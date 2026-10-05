import { RASHIS, ordinal } from "../format";

export interface ChartEntry {
  name: string;
  abbr: string;
  house: number; // 1..12 relative to the chart's Lagna
  degreeLabel?: string;
  retrograde?: boolean;
  dignity?: string;
  combust?: boolean;
}

interface Props {
  lagnaSign: number; // 0 = Aries
  entries: ChartEntry[];
  title?: string;
  subtitle?: string;
  showDegrees?: boolean;
  lagnaDegree?: string;
}

// North Indian (diamond) chart. House 1 is the top central diamond and houses
// run counter-clockwise. Signs move; houses are fixed.
const C = { x: 200, y: 200 };
const POLY: Record<number, [number, number][]> = {
  1: [[200, 0], [300, 100], [200, 200], [100, 100]],
  2: [[0, 0], [200, 0], [100, 100]],
  3: [[0, 0], [100, 100], [0, 200]],
  4: [[0, 200], [100, 100], [200, 200], [100, 300]],
  5: [[0, 200], [100, 300], [0, 400]],
  6: [[0, 400], [100, 300], [200, 400]],
  7: [[200, 400], [100, 300], [200, 200], [300, 300]],
  8: [[200, 400], [300, 300], [400, 400]],
  9: [[400, 400], [300, 300], [400, 200]],
  10: [[400, 200], [300, 300], [200, 200], [300, 100]],
  11: [[400, 200], [300, 100], [400, 0]],
  12: [[400, 0], [300, 100], [200, 0]],
};
// Where planet labels are centred, and where the sign number sits.
const CENTRE: Record<number, [number, number]> = {
  1: [200, 92], 2: [100, 30], 3: [36, 100], 4: [100, 192], 5: [36, 300], 6: [100, 362],
  7: [200, 292], 8: [300, 362], 9: [364, 300], 10: [300, 192], 11: [364, 100], 12: [300, 30],
};
const SIGN_POS: Record<number, [number, number]> = {
  1: [200, 180], 2: [100, 84], 3: [84, 104], 4: [182, 204], 5: [84, 304], 6: [100, 326],
  7: [200, 234], 8: [300, 326], 9: [318, 304], 10: [218, 204], 11: [318, 104], 12: [300, 84],
};
const TRIANGLE = new Set([2, 3, 5, 6, 8, 9, 11, 12]);

function marker(e: ChartEntry): string {
  let m = "";
  if (e.dignity === "exalted") m += "↑";
  if (e.dignity === "debilitated") m += "↓";
  if (e.retrograde && e.name !== "Rahu" && e.name !== "Ketu") m += "ᴿ";
  if (e.combust) m += "ᶜ";
  return m;
}

export default function KundaliChart({ lagnaSign, entries, title, subtitle, showDegrees = true, lagnaDegree }: Props) {
  const byHouse: Record<number, ChartEntry[]> = {};
  for (const e of entries) (byHouse[e.house] ||= []).push(e);

  return (
    <figure className="kundali-figure">
      {title && (
        <figcaption>
          <span className="kundali-title">{title}</span>
          {subtitle && <span className="kundali-sub">{subtitle}</span>}
        </figcaption>
      )}
      <svg viewBox="-4 -4 408 408" className="kundali-svg" role="img"
        aria-label={`${title ?? "Kundali"} chart with ${RASHIS[lagnaSign]} Lagna`}>
        <rect x="0" y="0" width="400" height="400" className="k-bg" />
        {Object.entries(POLY).map(([h, pts]) => (
          <polygon key={h} points={pts.map((p) => p.join(",")).join(" ")}
            className={Number(h) === 1 ? "k-house k-lagna" : "k-house"} />
        ))}
        <rect x="0" y="0" width="400" height="400" className="k-frame" />
        {Array.from({ length: 12 }, (_, i) => i + 1).map((h) => {
          const sign = (lagnaSign + h - 1) % 12;
          const [sx, sy] = SIGN_POS[h];
          return (
            <text key={`s${h}`} x={sx} y={sy} className="k-sign" textAnchor="middle" dominantBaseline="middle">
              <title>{`${ordinal(h)} house: ${RASHIS[sign]}`}</title>
              {sign + 1}
            </text>
          );
        })}
        {Array.from({ length: 12 }, (_, i) => i + 1).map((h) => {
          const list = byHouse[h] || [];
          const [cx, cy] = CENTRE[h];
          const n = list.length;
          const twoCol = n > (TRIANGLE.has(h) ? 2 : 3);
          const perLine = twoCol ? 2 : 1;
          const lines: ChartEntry[][] = [];
          for (let i = 0; i < n; i += perLine) lines.push(list.slice(i, i + perLine));
          const lh = twoCol ? 15 : 17;
          const fs = twoCol || n > 3 ? 11.5 : 13;
          let startY = cy - ((lines.length - 1) * lh) / 2;
          if (h === 1) startY = Math.min(Math.max(startY, 52), 120 - (lines.length - 1) * lh);
          if (h === 2 || h === 12) startY = 22;
          if (h === 6 || h === 8) startY = 378 - (lines.length - 1) * lh;
          return (
            <g key={`p${h}`}>
              {h === 1 && (
                <text x={200} y={156} className="k-asc" textAnchor="middle">
                  Lagna{lagnaDegree ? ` ${lagnaDegree}` : ""}
                </text>
              )}
              {lines.map((line, li) => (
                <text key={li} x={cx} y={startY + li * lh} textAnchor="middle"
                  dominantBaseline="middle" className="k-planet" style={{ fontSize: fs }}>
                  {line.map((e, ei) => (
                    <tspan key={e.name} className={e.retrograde && e.name !== "Rahu" && e.name !== "Ketu" ? "k-retro" : undefined}
                      dx={ei > 0 ? 6 : 0}>
                      <title>{`${e.name}${e.degreeLabel ? " " + e.degreeLabel : ""}${e.retrograde ? " (retrograde)" : ""}${e.dignity ? ", " + e.dignity : ""}`}</title>
                      {e.abbr}
                      {showDegrees && e.degreeLabel ? <tspan className="k-deg">{" " + e.degreeLabel}</tspan> : null}
                      {marker(e)}
                    </tspan>
                  ))}
                </text>
              ))}
            </g>
          );
        })}
        <circle cx={C.x} cy={C.y} r="2" className="k-centre" />
      </svg>
      <p className="kundali-legend">
        Numbers are rashis (1 Aries … 12 Pisces). ↑ exalted · ↓ debilitated · ᴿ retrograde · ᶜ combust
      </p>
    </figure>
  );
}
