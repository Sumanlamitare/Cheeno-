import { useEffect, useState } from "react";
import { ApiError, generateKundali, type KundaliRequest } from "./api";
import BirthForm from "./components/BirthForm";
import Results from "./components/Results";
import type { Report } from "./types";

export default function App() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ message: string; field: string | null } | null>(null);

  useEffect(() => {
    document.title = report ? `Janma Kundali${report.birth.name ? " · " + report.birth.name : ""}` : "Janma Kundali";
  }, [report]);

  async function submit(req: KundaliRequest) {
    setLoading(true);
    setError(null);
    try {
      const r = await generateKundali(req);
      setReport(r);
      window.scrollTo({ top: 0 });
    } catch (e) {
      if (e instanceof ApiError) setError({ message: e.message, field: e.field });
      else setError({ message: "The server could not be reached. Please try again.", field: null });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="masthead no-print">
        <a className="brand" href="/" onClick={(e) => { e.preventDefault(); setReport(null); }}>
          <svg viewBox="0 0 40 40" aria-hidden="true" className="brand-mark">
            <rect x="2" y="2" width="36" height="36" fill="none" stroke="currentColor" strokeWidth="2" />
            <path d="M2 2 L38 38 M38 2 L2 38 M20 2 L38 20 L20 38 L2 20 Z" fill="none" stroke="currentColor" strokeWidth="2" />
          </svg>
          <span>
            <span className="brand-name">Janma Kundali</span>
            <span className="brand-dev" lang="ne">जन्म कुण्डली</span>
          </span>
        </a>
        <span className="masthead-note">Sidereal · Lahiri · Whole Sign · Swiss Ephemeris</span>
      </header>
      {report ? (
        <Results report={report} onNew={() => { setReport(null); setError(null); }} />
      ) : (
        <main className="landing">
          <div className="landing-intro">
            <p className="eyebrow">Janma Patrika · Chino</p>
            <h1>A traditional Nepali birth chart, calculated precisely and explained rule by rule.</h1>
            <p className="lead">
              Enter the birth date, time and place. The chart is computed with the Swiss Ephemeris in the sidereal
              zodiac (Lahiri ayanamsha), and every interpretation comes from explicit classical Jyotish rules, each
              with a <em>Why?</em> showing the exact placements behind it.
            </p>
            <ul className="landing-points">
              <li>Rashi, Navamsa and Dashamsha charts in the North Indian style</li>
              <li>Panchanga, Vimshottari Dasha, Gochar and Sade Sati</li>
              <li>Yogas and Doshas with their defining conditions</li>
              <li>Bikram Sambat and AD dates, historical timezones worldwide</li>
            </ul>
          </div>
          <div className="landing-form card">
            <h2>Birth details</h2>
            <BirthForm onSubmit={submit} loading={loading} serverError={error} />
          </div>
        </main>
      )}
      <footer className="site-footer">
        <p>Jyotish is a traditional astrological system. Its interpretations are cultural and spiritual frameworks and are
          not scientifically validated predictions. This reading should not replace professional medical, financial, legal
          or other expert advice.</p>
        <p className="muted small">No AI is used. No data is stored. Calculations: Swiss Ephemeris © Astrodienst AG (AGPL).</p>
      </footer>
    </div>
  );
}
