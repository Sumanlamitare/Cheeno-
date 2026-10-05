// Shapes of the API report (kept intentionally loose where the UI only renders values).

export interface Place {
  id: string;
  name: string;
  label: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone: string;
  source: string;
}

export interface DualDate {
  ad: string;
  adLabel: string;
  bs: string | null;
  bsLabel: string | null;
  bsLabelDevanagari: string | null;
  bsAvailable: boolean;
}

export interface VargaPos {
  sign: number;
  signName: string;
  house: number;
  dignity: string;
}

export interface PlanetPos {
  name: string;
  sanskrit: string;
  abbr: string;
  longitude: number;
  sign: number;
  signName: string;
  degree: number;
  degreeLabel: string;
  nakshatra: number;
  nakshatraName: string;
  nakshatraLord: string;
  pada: number;
  house: number;
  retrograde: boolean;
  motion: string;
  speed: number;
  combust: boolean;
  sunDistance: number;
  dignity: string;
  benefic: boolean;
  vargas: Record<string, VargaPos>;
}

export interface Group {
  theme: string;
  label: string;
  polarity: string;
  weight: number;
  strength: string;
  text: string;
  supporting: string[];
  why: string[];
  modifiers: string[];
  ruleIds: string[];
  sources: string[];
}

export interface TimingWindow {
  mahadasha: string;
  antardasha: string;
  start: string;
  end: string;
  level: string;
  why: string[];
  jupiterSupport?: boolean;
}

export interface Reading {
  topic: string;
  emphasis: string;
  balance: number | null;
  overall: string;
  overallWhy: string[];
  strengths: Group[];
  challenges: Group[];
  notes: Group[];
  keyFactors?: { label: string; value: string }[];
  timing?: { windows: TimingWindow[]; method: string };
  disclaimer?: string;
  [k: string]: unknown;
}

export interface Item {
  text: string;
  polarity?: string;
  why: string[];
  ruleId?: string;
}

export interface DashaPeriod {
  lord: string;
  start: string;
  end: string;
  durationYears: number;
  status: "past" | "current" | "upcoming";
  level: number;
  beforeBirth: boolean;
  children?: DashaPeriod[];
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Report = any;
