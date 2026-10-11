import { useCallback, useEffect, useState } from 'react';
import { Indicator, Publication, ScrapeStatus } from './types';
import { FALLBACK_INDICATORS, FALLBACK_PUBLICATIONS, FALLBACK_STATUS } from './fallbackData';

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
  /** True si se están mostrando datos de fallback porque la API no respondió */
  isOffline: boolean;
}

/**
 * Carga datos de la API al montar el componente.
 * Si la API no responde (network error), usa datos de fallback reales
 * para que la UI siga siendo funcional en modo demo/offline.
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  fallback?: T
): ApiState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setIsOffline(false);
    fetcher()
      .then(result => {
        if (!cancelled) {
          setData(result);
          setIsOffline(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const msg = err instanceof Error ? err.message : String(err);
          // Si es un error de red y tenemos fallback, lo usamos silenciosamente
          const isNetworkError = msg.includes('Failed to fetch')
            || msg.includes('NetworkError')
            || msg.includes('network')
            || msg.includes('fetch')
            || msg.includes('Load failed')
            || msg.includes('aborted');

          if (isNetworkError && fallback !== undefined) {
            setData(fallback);
            setIsOffline(true);
            setError(null);
          } else {
            setError(msg);
            setIsOffline(false);
          }
        }
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [fetcher, attempt]);

  const reload = useCallback(() => setAttempt(a => a + 1), []);
  return { data, error, loading, reload, isOffline };
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
