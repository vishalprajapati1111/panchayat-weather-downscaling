export interface DailyResponse {
  village_id: string;
  name: string;
  state: string;
  lat: number;
  lon: number;
  elevation_m: number;
  forecast_date: string;
  cell_precip_sum_mm: number;
  rain_ratio: number;
  wind_dir_deg: number;
  wind_speed_max_kmh: number;
  gate_g: number;
  effective_ratio: number;
  rain_mm: number;
  cell_tmax_c: number;
  cell_tmin_c: number;
  temp_offset_c: number;
  tmax_c: number;
  tmin_c: number;
  tmean_c: number;
  eto_mm_day: number;
  inside_validated_band: boolean;
  distance_km: number;
  in_domain: boolean;
  driver_model: string;
  driver_source: string;
}

export interface PredictResponse {
  village_id: string;
  name: string;
  village_name: string;
  state: string;
  lat: number;
  lon: number;
  elevation_m: number;
  temp_c: number;
  eto_mm_day: number;
  rainfall_jjas_mm: number;
  inside_validated_band: boolean;
  distance_km: number;
  in_domain: boolean;
  note: string;
}

export interface SearchResultItem {
  village_id: string;
  name: string;
  state: string;
  lat: number;
  lon: number;
  type?: 'gauge' | 'village';
}

export interface ModelInfoResponse {
  rainfall: {
    median_ape_pct: number;
    unanchored_mape_pct: number;
    windward_mape_pct: number;
    leeward_mape_pct: number;
    n_gauges: number;
    domain_band: string;
    n_villages_in_band: number;
    n_villages_total: number;
  };
  temperature: {
    method: string;
    validation_split: string;
    stations: string[];
    loso_mae_baseline_c: number;
    loso_mae_corrected_c: number;
    pct_improvement: number;
    note: string;
  };
}

export const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8000';

export async function predict(lat: number, lon: number): Promise<PredictResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/api/predict?lat=${lat}&lon=${lon}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error('AgroMet predict error:', e);
    return null;
  }
}

export async function daily(lat: number, lon: number): Promise<DailyResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/api/daily?lat=${lat}&lon=${lon}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error('AgroMet daily error:', e);
    return null;
  }
}

export async function search(q: string): Promise<SearchResultItem[] | null> {
  try {
    const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(q)}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error('AgroMet search error:', e);
    return null;
  }
}

export async function modelInfo(): Promise<ModelInfoResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/api/model_info`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error('AgroMet modelInfo error:', e);
    return null;
  }
}
