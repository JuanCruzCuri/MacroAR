import { useCallback, useEffect, useState } from 'react';
import { Indicator, Publication, ScrapeStatus } from './types';
import { DEMO_INDICATORS, DEMO_PUBLICATIONS } from './demoData';

export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status} en ${path}`);
  return res.json() as Promise<T>;
}

export const fetchIndicators = () => getJSON<Indicator[]>('/api/indicators');
export const fetchPublications = () => getJSON<Publication[]>('/api/publications?limit=100');
export const fetchStatus = () => getJSON<ScrapeStatus>('/api/meta/status');

interface ApiState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
  isDemo?: boolean;
}

/** Carga datos de la API al montar el componente. Si falla, usa datos de demo. */
export function useApi<T>(fetcher: () => Promise<T>, demoData?: T): ApiState<T> {
  const [data, setData] = useState<T | null>(demoData || null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(!demoData);
  const [attempt, setAttempt] = useState(0);
  const [isDemo, setIsDemo] = useState(!!demoData);

  useEffect(() => {
    let cancelled = false;
    
    // Si hay datos de demo, mostrarlos inmediatamente
    if (demoData) {
      setData(demoData);
      setIsDemo(true);
      setLoading(false);
    } else {
      setLoading(true);
    }
    
    setError(null);
    
    // Intentar cargar desde la API
    fetcher()
      .then(result => {
        if (!cancelled) {
          setData(result);
          setIsDemo(false);
          setError(null);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          // Si tenemos datos de demo, no mostrar error
          if (demoData) {
            console.log('API no disponible, usando datos de demo');
            setIsDemo(true);
          } else {
            setError(err instanceof Error ? err.message : String(err));
          }
        }
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    
    return () => { cancelled = true; };
  }, [fetcher, attempt]);

  const reload = useCallback(() => setAttempt(a => a + 1), []);
  return { data, error, loading, reload, isDemo };
}

/** ISO → "11 de octubre de 2026, 18:00 ART" (siempre en hora argentina). */
export function formatDateTimeART(iso: string | null | undefined): string | null {
  if (!iso) return null;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return null;
  const formatted = date.toLocaleString('es-AR', {
    timeZone: 'America/Argentina/Buenos_Aires',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
  return `${formatted} ART`;
}
