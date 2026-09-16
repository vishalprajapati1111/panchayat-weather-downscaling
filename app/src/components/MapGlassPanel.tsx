import React from 'react';
import { PredictResponse, DailyResponse } from '../services/agromet';

interface MapGlassPanelProps {
  prediction: PredictResponse | null;
  dailyForecast?: DailyResponse | null;
  loading: boolean;
  domainFallbackNote?: string | null;
  isMobile?: boolean;
}

export const MapGlassPanel: React.FC<MapGlassPanelProps> = ({
  prediction,
  dailyForecast,
  loading,
  domainFallbackNote,
  isMobile = false,
}) => {
  const villageName = dailyForecast?.name || prediction?.name || prediction?.village_name || '–';
  const state = dailyForecast?.state || prediction?.state || '–';
  
  // Live Forecast fields (/api/daily)
  const forecastDate = dailyForecast?.forecast_date || 'tomorrow';
  const liveRainStr = dailyForecast?.rain_mm != null ? `${dailyForecast.rain_mm.toFixed(1)} mm` : '–';
  const liveTmaxTminStr = dailyForecast ? `${dailyForecast.tmax_c.toFixed(1)}° / ${dailyForecast.tmin_c.toFixed(1)}°C` : '–';
  const liveEtoStr = dailyForecast?.eto_mm_day != null ? `${dailyForecast.eto_mm_day.toFixed(1)} mm/d` : '–';

  // Seasonal JJAS fields (/api/predict)
  const seasonalTempStr = prediction?.temp_c != null ? `${prediction.temp_c.toFixed(1)}°C` : '–';
  const seasonalEtoStr = prediction?.eto_mm_day != null ? `${prediction.eto_mm_day.toFixed(1)} mm/d` : '–';
  const seasonalRainStr = prediction?.rainfall_jjas_mm != null ? `${Math.round(prediction.rainfall_jjas_mm)} mm` : '–';
  const elevationStr = (dailyForecast?.elevation_m ?? prediction?.elevation_m) != null 
    ? `${(dailyForecast?.elevation_m ?? prediction?.elevation_m)!.toFixed(0)} m` 
    : '–';
  const isValidated = (dailyForecast?.inside_validated_band ?? prediction?.inside_validated_band) ?? false;

  return (
    <div
      className="pointer-events-auto select-none"
      style={{
        position: 'fixed',
        top: isMobile ? '72px' : '16px',
        right: '16px',
        width: isMobile ? '56vw' : '330px',
        maxWidth: isMobile ? '240px' : '330px',
        zIndex: 20,
        background: 'rgba(255, 255, 255, 0.90)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderRadius: '14px',
        boxShadow: '0 4px 24px rgba(0, 0, 0, 0.12)',
        border: '1px solid rgba(255, 255, 255, 0.7)',
        padding: isMobile ? '10px 12px' : '14px 16px',
      }}
    >
      {/* Domain fallback note if triggered */}
      {domainFallbackNote && prediction?.in_domain === false && (
        <div className="mb-2 px-2 py-0.5 rounded-md bg-amber-50 border border-amber-200 text-amber-800 text-[10px] leading-tight font-medium">
          {domainFallbackNote}
        </div>
      )}

      {/* Location Header */}
      <div className="flex items-start justify-between gap-1.5 mb-1.5">
        <div className="min-w-0 flex-1">
          <h2 className={`${isMobile ? 'text-sm' : 'text-base'} font-bold text-neutral-900 truncate leading-tight`}>
            {villageName}
          </h2>
          <p className="text-[11px] text-neutral-500 font-medium truncate">
            {state} • Elev: {elevationStr}
          </p>
        </div>
        {loading && (
          <span className="material-symbols-outlined text-[14px] text-neutral-400 animate-spin shrink-0">
            progress_activity
          </span>
        )}
      </div>

      {/* LIVE NUMERICAL FORECAST (Open-Meteo ECMWF IFS live driver) */}
      <div className="rounded-lg bg-emerald-50/80 border border-emerald-200/80 p-2 my-1.5">
        <div className="text-[9px] md:text-[10px] font-bold text-emerald-800 uppercase tracking-wider mb-1 truncate">
          ECMWF IFS 0.25° · forecast for {forecastDate}
        </div>
        <div className="flex items-baseline justify-between">
          <div>
            <div className="text-xl md:text-2xl font-black text-neutral-900 leading-tight">
              {liveRainStr}
            </div>
            <div className="text-[10px] font-semibold text-emerald-900">
              Disaggregated Rain
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs md:text-sm font-bold text-neutral-800">
              {liveTmaxTminStr}
            </div>
            <div className="text-[10px] text-neutral-600 font-medium">
              ETo: <span className="font-semibold text-neutral-800">{liveEtoStr}</span>
            </div>
          </div>
        </div>
      </div>

      {/* SEASONAL NORMAL (JJAS / ERA5 Reanalysis) */}
      <div className="pt-1.5 pb-1 text-[10px] md:text-[11px] text-neutral-600">
        <div className="font-semibold text-neutral-500 uppercase text-[9px] tracking-wider mb-0.5">
          seasonal normal (JJAS)
        </div>
        <div className="flex items-center justify-between font-medium text-neutral-700">
          <span>Temp: <strong className="text-neutral-900">{seasonalTempStr}</strong></span>
          <span>Rain: <strong className="text-neutral-900">{seasonalRainStr}</strong></span>
          <span>ETo: <strong className="text-neutral-900">{seasonalEtoStr}</strong></span>
        </div>
      </div>

      {/* Validation Band Badge */}
      <div className="mt-2 pt-2 border-t border-neutral-200/60 flex items-center justify-between">
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] md:text-[10px] font-semibold ${
            isValidated
              ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
              : 'bg-amber-100 text-amber-800 border border-amber-300'
          }`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full shrink-0 ${
              isValidated ? 'bg-emerald-600' : 'bg-amber-600'
            }`}
          />
          <span className="truncate">
            {isMobile
              ? (isValidated ? 'Validated' : 'Extrapolated')
              : (isValidated ? 'Gauge-validated band' : 'Outside band — extrapolated')}
          </span>
        </span>

        {!isMobile && (dailyForecast?.distance_km ?? prediction?.distance_km) != null && (
          <span className="text-[10px] text-neutral-400 font-mono">
            {(dailyForecast?.distance_km ?? prediction?.distance_km)!.toFixed(1)} km
          </span>
        )}
      </div>
    </div>
  );
};
