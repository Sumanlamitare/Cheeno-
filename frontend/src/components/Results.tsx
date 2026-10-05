import { useEffect, useState } from "react";
import { fmtLatLon } from "../format";
import type { Report } from "../types";
import { Section, ReadingView } from "./common";
import { DashaTable, LifeTimeline } from "./Dasha";
import Explained from "./Explained";
import Houses from "./Houses";
import KundaliChart from "./KundaliChart";
import PlanetTable, { ShadbalaTable } from "./Planets";
import {
  CalculationDetails, CareerExtras, CurrentDasha, DoshasSection, HealthExtras, LagnaSection, MoonSection,
  PanchangaSection, YogasSection,
} from "./Sections";
import { Gochar, SadeSati } from "./Transits";
import { AdvancedVargas, VargaSection } from "./Vargas";

const NAV: [string, string][] = [
  ["explained", "Explained"], ["d1", "Rashi Chart"], ["planets", "Planets"], ["lagna", "Lagna"], ["moon", "Rashi & Nakshatra"], ["houses", "Houses"],
  ["career", "Career"], ["wealth", "Wealth"], ["education", "Education"], ["marriage", "Marriage"], ["family", "Family"],
  ["travel", "Travel"], ["children", "Children"], ["health", "Health"], ["yogas", "Yogas"], ["doshas", "Doshas"],
  ["dasha", "Dasha"], ["gochar", "Gochar"], ["sadesati", "Sade Sati"], ["d9", "Navamsa"], ["d10", "Dashamsha"],
  ["panchanga", "Panchanga"], ["calc", "Calculation"],
];

export default function Results({ report, onNew }: { report: Report; onNew: () => void }) {
  const [active, setActive] = useState("explained");
  const s = report.summary;
  const b = report.birth;
  const i = report.interpretation;

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        const vis = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (vis[0]) setActive(vis[0].target.id);
      },
      { rootMargin: "-20% 0px -70% 0px" },
    );
    NAV.forEach(([id]) => { const el = document.getElementById(id); if (el) obs.observe(el); });
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    // Expand every collapsible block for printing, then restore.
    let opened: HTMLDetailsElement[] = [];
    const before = () => {
      opened = Array.from(document.querySelectorAll("details:not([open])")) as HTMLDetailsElement[];
      opened.forEach((d) => (d.open = true));
    };
    const after = () => opened.forEach((d) => (d.open = false));
    window.addEventListener("beforeprint", before);
    window.addEventListener("afterprint", after);
    return () => { window.removeEventListener("beforeprint", before); window.removeEventListener("afterprint", after); };
  }, []);

  const d1Entries = report.chart.planets.map((p: any) => ({
    name: p.name, abbr: p.abbr, house: p.house, degreeLabel: `${Math.floor(p.degree)}°`,
    retrograde: p.retrograde, dignity: p.dignity, combust: p.combust,
  }));

  return (
    <main className="results">
      <div className="report-hero">
        <div>
          <p className="eyebrow">Janma Kundali · जन्म कुण्डली</p>
          <h1>{b.name ? `${b.name}'s Janma Kundali` : "Your Janma Kundali"}</h1>
          <dl className="birth-info">
            <div><dt>Birth date</dt><dd>{b.date.bsLabel && <>{b.date.bsLabel} <span className="dev">({b.date.bsLabelDevanagari})</span><br /></>}{b.date.adLabel}</dd></div>
            <div><dt>Birth time</dt><dd>{b.time12} <span className="muted">({b.time})</span>{b.timeAccuracy === "approximate" && <><br /><span className="warn-text">Reported as approximate</span></>}</dd></div>
            <div><dt>Birthplace</dt><dd>{b.place.label}<br /><span className="muted small">{fmtLatLon(b.place.latitude, b.place.longitude)}</span></dd></div>
            <div><dt>Timezone</dt><dd>{b.timezone.tzName}<br /><span className="muted small">{b.timezone.offsetLabel}{b.timezone.dst ? " (daylight saving)" : ""}</span></dd></div>
          </dl>
        </div>
        <div className="hero-actions no-print">
          <button type="button" className="primary" onClick={() => window.print()}>Download Kundali</button>
          <button type="button" className="secondary" onClick={onNew}>New chart</button>
          <p className="small muted">Download opens the print dialog; choose "Save as PDF".</p>
        </div>
      </div>

      {report.warnings.length > 0 && (
        <div className="warnings" role="note">
          {report.warnings.map((w: string, k: number) => <p key={k}>{w}</p>)}
        </div>
      )}

      <section className="quick-summary" aria-label="Quick summary">
        {[
          ["Lagna", `${s.lagna}`, s.lagnaDegree], ["Janma Rashi", s.janmaRashi, "Moon sign"],
          ["Nakshatra", s.nakshatra, `Lord ${s.nakshatraLord}`], ["Pada", String(s.pada), ""],
          ["Mahadasha", s.currentMahadasha ?? "—", "current"], ["Antardasha", s.currentAntardasha ?? "—", "current"],
          ["Sade Sati", s.sadeSati, ""],
        ].map(([k, v, sub]) => (
          <div key={k} className="qs-item"><span className="eyebrow">{k}</span><strong>{v}</strong>{sub && <span className="muted small">{sub}</span>}</div>
        ))}
      </section>

      <nav className="section-nav no-print" aria-label="Report sections">
        {NAV.map(([id, label]) => (
          <a key={id} href={`#${id}`} className={active === id ? "active" : ""}>{label}</a>
        ))}
      </nav>

      <div className="report-body">
        <Section id="explained" num="★" title="Your Kundali Explained" kicker="A plain-language walkthrough. The detailed classical sections follow below.">
          <Explained report={report} />
        </Section>

        <Section id="d1" num={1} title="Rashi Chart (D1)" kicker="Janma Kundali in the North Indian style">
          <div className="chart-centre">
            <KundaliChart lagnaSign={report.chart.ascendant.sign} entries={d1Entries} title="Rashi · D1"
              subtitle={`${s.lagna} Lagna`} lagnaDegree={`${Math.floor(report.chart.ascendant.degree)}°`} />
          </div>
        </Section>

        <Section id="planets" num={2} title="Planetary Positions" kicker="Navagraha in the sidereal zodiac. Select Explain for the traditional significance.">
          <PlanetTable report={report} />
          <h3 className="col-title">Planetary strength (Shadbala)</h3>
          <ShadbalaTable report={report} />
        </Section>

        <Section id="lagna" num={3} title="Lagna & Core Nature"><LagnaSection report={report} /></Section>
        <Section id="moon" num={4} title="Janma Rashi & Nakshatra"><MoonSection report={report} /></Section>
        <Section id="houses" num={5} title="The Twelve Bhavas"><Houses report={report} /></Section>

        <Section id="career" num={6} title="Career" kicker="10th house, its lord, D10, Dashas and transits">
          <ReadingView r={i.career} /><CareerExtras report={report} />
        </Section>
        <Section id="wealth" num={7} title="Wealth" kicker="2nd, 5th, 9th and 11th houses, Jupiter, Venus and Dhana yogas">
          <ReadingView r={i.wealth} />
        </Section>
        <Section id="education" num={8} title="Education" kicker="4th, 5th and 9th houses, Mercury and Jupiter">
          <ReadingView r={i.education} />
        </Section>
        <Section id="marriage" num={9} title="Love & Marriage" kicker="7th house, Venus, Jupiter, Moon and the Navamsa">
          <ReadingView r={i.marriage} />
        </Section>
        <Section id="family" num={10} title="Family & Home" kicker="2nd and 4th houses and the Moon">
          <ReadingView r={i.family} />
        </Section>
        <Section id="travel" num={11} title="Travel & Relocation" kicker="3rd, 9th and 12th houses, Rahu and the 4th lord">
          <ReadingView r={i.travel} />
        </Section>
        <Section id="children" num="11a" title="Children" kicker="5th house, its lord, Jupiter and the Saptamsha (D7)">
          <ReadingView r={i.children} />
        </Section>
        <Section id="health" num="11b" title="Health (traditional tendencies)" kicker="Not medical advice">
          <ReadingView r={i.health} /><HealthExtras report={report} />
        </Section>

        <Section id="yogas" num={12} title="Yogas"><YogasSection report={report} /></Section>
        <Section id="doshas" num={13} title="Doshas"><DoshasSection report={report} /></Section>

        <Section id="dasha" num={14} title="Vimshottari Dasha" kicker="Calculated from the Moon's nakshatra at birth">
          <h3 className="col-title">Life timeline</h3>
          <LifeTimeline report={report} />
          <h3 className="col-title">Current life period</h3>
          <CurrentDasha report={report} />
          <h3 className="col-title">Mahadasha periods</h3>
          <DashaTable report={report} />
        </Section>

        <Section id="gochar" num={15} title="Current Gochar (Transits)"><Gochar report={report} /></Section>
        <Section id="sadesati" num={16} title="Sade Sati"><SadeSati report={report} /></Section>
        <Section id="d9" num={17} title="Navamsa (D9)"><VargaSection report={report} division={9} /></Section>
        <Section id="d10" num={18} title="Dashamsha (D10)">
          <VargaSection report={report} division={10} />
          <AdvancedVargas report={report} />
        </Section>
        <Section id="panchanga" num={19} title="Birth Panchanga"><PanchangaSection report={report} /></Section>
        <Section id="calc" num={20} title="Calculation Details"><CalculationDetails report={report} /></Section>

        <p className="disclaimer">{report.disclaimer}</p>
      </div>
    </main>
  );
}
