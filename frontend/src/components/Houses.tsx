import { useState } from "react";
import { cap, ordinal } from "../format";
import type { Report } from "../types";
import { Badge, ItemList, Why } from "./common";

export default function Houses({ report }: { report: Report }) {
  const houses = report.interpretation.houses;
  const [open, setOpen] = useState<number | null>(1);
  return (
    <div className="houses">
      {houses.map((h: any) => (
        <article key={h.house} className={`house-card ${open === h.house ? "open" : ""}`}>
          <button type="button" className="house-toggle" aria-expanded={open === h.house}
            onClick={() => setOpen(open === h.house ? null : h.house)}>
            <span className="house-num">{h.house}</span>
            <span className="house-title">
              <strong>{ordinal(h.house)} House · {h.name}</strong>
              <span className="muted">{h.topics}</span>
            </span>
            <span className="house-sign">{h.signName}</span>
            <Badge tone={h.strength === "Strong" ? "good" : h.strength === "Weak" ? "warn" : "neutral"}>{h.strength}</Badge>
          </button>
          {open === h.house && (
            <div className="house-body">
              <dl className="mini-dl">
                <div><dt>Sign</dt><dd>{h.signName}</dd></div>
                <div><dt>Lord</dt><dd>{h.lord} in the {ordinal(h.lordHouse)} house ({h.lordSign}, {h.lordDignity})</dd></div>
                <div><dt>Occupants</dt><dd>{h.occupants.length ? h.occupants.join(", ") : "None"}</dd></div>
                <div><dt>Aspects</dt><dd>{h.aspects.length ? h.aspects.map((a: any) => `${a.planet} (${ordinal(a.aspect)})`).join(", ") : "None"}</dd></div>
                <div><dt>Yogas</dt><dd>{h.yogas.length ? h.yogas.map((y: any) => `${y.name} (${y.strength.toLowerCase()})`).join(", ") : "None"}</dd></div>
              </dl>
              <ItemList items={h.interpretation} />
              <Why label={`Strength assessment: ${cap(h.strength)} (${h.strengthScore})`} reasons={h.strengthWhy} />
            </div>
          )}
        </article>
      ))}
      <p className="small muted">{report.calculation.houseAssessment}</p>
    </div>
  );
}
