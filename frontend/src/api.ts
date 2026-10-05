import type { DualDate, Place, Report } from "./types";

export class ApiError extends Error {
  field: string | null;
  constructor(message: string, field: string | null) {
    super(message);
    this.field = field;
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (res.ok) return res.json() as Promise<T>;
  let message = "Something went wrong. Please try again.";
  let field: string | null = null;
  try {
    const body = await res.json();
    if (body?.detail?.message) {
      message = body.detail.message;
      field = body.detail.field ?? null;
    } else if (Array.isArray(body?.detail)) {
      message = "Please check the entered values.";
    }
  } catch {
    /* ignore */
  }
  throw new ApiError(message, field);
}

export async function searchPlaces(q: string, signal?: AbortSignal): Promise<Place[]> {
  const res = await fetch(`/api/places?q=${encodeURIComponent(q)}&limit=8`, { signal });
  return (await handle<{ results: Place[] }>(res)).results;
}

export async function placeFromCoordinates(lat: number, lon: number): Promise<Place> {
  const res = await fetch(`/api/places/coordinates?lat=${lat}&lon=${lon}`);
  return handle<Place>(res);
}

export async function convertDate(calendar: "AD" | "BS", date: string, signal?: AbortSignal): Promise<DualDate> {
  const res = await fetch("/api/convert-date", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ calendar, date }),
    signal,
  });
  return handle<DualDate>(res);
}

export interface KundaliRequest {
  name?: string;
  calendar: "AD" | "BS";
  date: string;
  time: string;
  meridiem?: "AM" | "PM";
  timeAccuracy: "exact" | "approximate";
  placeId?: string;
  latitude?: number;
  longitude?: number;
  placeLabel?: string;
  utcOffsetOverride?: number;
}

export async function generateKundali(req: KundaliRequest): Promise<Report> {
  const res = await fetch("/api/kundali", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return handle<Report>(res);
}
