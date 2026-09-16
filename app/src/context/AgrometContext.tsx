import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { predict, daily, modelInfo as fetchModelInfo, PredictResponse, DailyResponse, ModelInfoResponse } from '../services/agromet';

interface AgrometContextValue {
  prediction: PredictResponse | null;
  dailyForecast: DailyResponse | null;
  modelInfo: ModelInfoResponse | null;
  loading: boolean;
  error: string | null;
  currentCoords: { lat: number; lon: number };
  isOutOfDomain: boolean;
  domainFallbackNote: string | null;
  setLocation: (lat: number, lon: number) => Promise<void>;
  requestLocation: () => void;
  gpsStatus: string;
}

const DEFAULT_COORDS = { lat: 16.700, lon: 74.233 }; // Kolhapur
const DOMAIN = { latMin: 12.948, latMax: 17.550, lonMin: 73.448, lonMax: 76.552 };

const AgrometContext = createContext<AgrometContextValue | undefined>(undefined);

export const AgrometProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [dailyForecast, setDailyForecast] = useState<DailyResponse | null>(null);
  const [modelInfoData, setModelInfoData] = useState<ModelInfoResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentCoords, setCurrentCoords] = useState(DEFAULT_COORDS);
  const [isOutOfDomain, setIsOutOfDomain] = useState<boolean>(false);
  const [domainFallbackNote, setDomainFallbackNote] = useState<string | null>(null);
  const [gpsStatus, setGpsStatus] = useState<string>('idle');

  // Ref tracking whether a genuine GPS fix (or explicit user selection) has succeeded
  const hasRealFix = React.useRef<boolean>(false);

  const fetchPredictionForLocation = useCallback(async (lat: number, lon: number) => {
    setLoading(true);
    setError(null);
    setCurrentCoords({ lat, lon });
    const [pred, dailyData] = await Promise.all([
      predict(lat, lon),
      daily(lat, lon)
    ]);
    if (pred) {
      setPrediction(pred);
      // Clear domain banner on any successful in-domain location
      if (pred.in_domain) {
        setIsOutOfDomain(false);
        setDomainFallbackNote(null);
      } else {
        setIsOutOfDomain(true);
        setDomainFallbackNote('showing Kolhapur — your location is outside the model domain');
      }
    } else {
      setError('Failed to load prediction from AgroMet API');
    }
    if (dailyData) {
      setDailyForecast(dailyData);
    }
    setLoading(false);
  }, []);

  const setLocation = useCallback(async (lat: number, lon: number) => {
    // Explicit user action marks hasRealFix to prevent late fallbacks from overwriting
    hasRealFix.current = true;
    await fetchPredictionForLocation(lat, lon);
  }, [fetchPredictionForLocation]);

  const requestLocation = useCallback(() => {
    if (!('geolocation' in navigator)) {
      setGpsStatus('GPS fail code 0 navigator.geolocation unavailable');
      if (!hasRealFix.current) {
        setIsOutOfDomain(false);
        setDomainFallbackNote(null);
        fetchPredictionForLocation(DEFAULT_COORDS.lat, DEFAULT_COORDS.lon);
      }
      return;
    }

    setGpsStatus('requesting…');

    const handleSuccess = (pos: GeolocationPosition) => {
      hasRealFix.current = true;
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      const acc = pos.coords.accuracy != null ? Math.round(pos.coords.accuracy) : 0;
      setGpsStatus(`GPS ok ${lat.toFixed(4)},${lon.toFixed(4)} acc ${acc}m`);

      const inside =
        lat >= DOMAIN.latMin &&
        lat <= DOMAIN.latMax &&
        lon >= DOMAIN.lonMin &&
        lon <= DOMAIN.lonMax;

      if (inside) {
        setIsOutOfDomain(false);
        setDomainFallbackNote(null);
        fetchPredictionForLocation(lat, lon);
      } else {
        console.log('GPS coords actually fell outside model domain:', lat, lon);
        setIsOutOfDomain(true);
        setDomainFallbackNote('showing Kolhapur — your location is outside the model domain');
        fetchPredictionForLocation(DEFAULT_COORDS.lat, DEFAULT_COORDS.lon);
      }
    };

    const handleAttempt2Error = (err: GeolocationPositionError) => {
      console.warn('GPS attempt 2 failed:', err.message);
      setGpsStatus(`GPS fail code ${err.code} ${err.message}`);
      // Kolhapur fallback must only ever run when GPS has definitively failed both attempts
      // and only if no real fix has succeeded
      if (!hasRealFix.current) {
        console.warn('Definitively failed both GPS attempts; falling back to Kolhapur default');
        setIsOutOfDomain(false);
        setDomainFallbackNote(null);
        fetchPredictionForLocation(DEFAULT_COORDS.lat, DEFAULT_COORDS.lon);
      }
    };

    const handleAttempt1Error = (err: GeolocationPositionError) => {
      console.warn('GPS attempt 1 failed, starting attempt 2:', err.message);
      if (hasRealFix.current) return;
      setGpsStatus('requesting…');
      // Attempt 2: low accuracy, timeout 15000ms, maximumAge 60000ms
      navigator.geolocation.getCurrentPosition(
        handleSuccess,
        handleAttempt2Error,
        { enableHighAccuracy: false, timeout: 15000, maximumAge: 60000 }
      );
    };

    // Attempt 1: high accuracy, timeout 8000ms, maximumAge 0
    navigator.geolocation.getCurrentPosition(
      handleSuccess,
      handleAttempt1Error,
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
  }, [fetchPredictionForLocation]);

  useEffect(() => {
    // 1. Fetch static model credentials once
    fetchModelInfo().then((info) => {
      if (info) setModelInfoData(info);
    });

    // 2. Initial position resolution via retry chain
    requestLocation();
  }, [requestLocation]);

  return (
    <AgrometContext.Provider
      value={{
        prediction,
        dailyForecast,
        modelInfo: modelInfoData,
        loading,
        error,
        currentCoords,
        isOutOfDomain,
        domainFallbackNote,
        setLocation,
        requestLocation,
        gpsStatus,
      }}
    >
      {children}
    </AgrometContext.Provider>
  );
};

export function useAgromet(): AgrometContextValue {
  const context = useContext(AgrometContext);
  if (!context) {
    throw new Error('useAgromet must be used within an AgrometProvider');
  }
  return context;
}
