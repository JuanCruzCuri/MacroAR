import { useState, useMemo } from 'react';
import { Publication } from '../types';
import { fetchPublications, useApi } from '../api';
import { FALLBACK_PUBLICATIONS } from '../fallbackData';
import ApiError from './ApiError';
import OfflineBanner from './OfflineBanner';

type SortOption = 'date_desc' | 'date_asc' | 'source';
type TypeFilter = 'all' | 'informe' | 'reporte' | 'analisis';

function getSourceColor(source: string): string {
  if (source.includes('INDEC')) return 'badge-blue';
  if (source.includes('CIF')) return 'badge-purple';
  if (source.includes('DGEC') || source.includes('GCBA')) return 'badge-green';
  if (source.includes('UCEMA')) return 'badge-amber';
  return 'badge-blue';
}

function getTypeIcon(type: string): string {
  switch (type) {
    case 'informe': return '📄';
    case 'reporte': return '📋';
    case 'analisis': return '🔍';
    default: return '📰';
  }
}

function getTypeLabel(type: string): string {
  switch (type) {
    case 'informe': return 'Informe';
    case 'reporte': return 'Reporte';
    case 'analisis': return 'Análisis';
    default: return type;
  }
}

function toTime(dateStr: string | null): number {
  return dateStr ? new Date(dateStr + 'T00:00:00').getTime() : 0;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '';
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
}

function getRelativeTime(dateStr: string | null): string {
  if (!dateStr) return '';
  const date = new Date(dateStr + 'T00:00:00');
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays <= 0) return 'Hoy';
  if (diffDays === 1) return 'Ayer';
  if (diffDays < 7) return `Hace ${diffDays} días`;
  if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
  return `Hace ${Math.floor(diffDays / 30)} meses`;
}

export default function Feed({ isOffline }: { isOffline: boolean }) {
  const [sourceFilter, setSourceFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all');
  const [sortBy, setSortBy] = useState<SortOption>('date_desc');
  const [latestOnly, setLatestOnly] = useState(false);
  const { data: publications, error, loading, reload } = useApi(fetchPublications, FALLBACK_PUBLICATIONS);
  
  const sources = useMemo(
    () => ['all', ...Array.from(new Set((publications ?? []).map(p => p.source))).sort()],
    [publications]
  );
  const types: { key: TypeFilter; label: string }[] = [
    { key: 'all', label: 'Todos los tipos' },
    { key: 'informe', label: '📄 Informes' },
    { key: 'reporte', label: '📋 Reportes' },
    { key: 'analisis', label: '🔍 Análisis' },
  ];

  // Apply filters and sorting
  const filteredPublications = useMemo(() => {
    let result = [...(publications ?? [])];
    
    // Filter by source
    if (sourceFilter !== 'all') {
      result = result.filter(p => p.source === sourceFilter);
    }
    
    // Filter by type
    if (typeFilter !== 'all') {
      result = result.filter(p => p.type === typeFilter);
    }
    
    // Filter latest only (most recent per source)
    if (latestOnly) {
      const latestBySource: Record<string, Publication> = {};
      // Sort by date first to get the latest
      result.sort((a, b) => toTime(b.date) - toTime(a.date));
      for (const pub of result) {
        if (!latestBySource[pub.source]) {
          latestBySource[pub.source] = pub;
        }
      }
      result = Object.values(latestBySource);
    }
    
    // Sort
    switch (sortBy) {
      case 'date_desc':
        result.sort((a, b) => toTime(b.date) - toTime(a.date));
        break;
      case 'date_asc':
        result.sort((a, b) => toTime(a.date) - toTime(b.date));
        break;
      case 'source':
        result.sort((a, b) => a.source.localeCompare(b.source));
        break;
    }
    
    return result;
  }, [publications, sourceFilter, typeFilter, sortBy, latestOnly]);

  return (
    <div>
      {/* Section Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">Feed de Publicaciones</h2>
        <p className="text-gray-400 text-sm">
          Últimos informes, reportes y análisis publicados por las fuentes monitoreadas.
          Ordenados cronológicamente con enlaces a los documentos originales.
        </p>
      </div>

      {/* Filter Controls */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 mb-6">
        {/* Row 1: Source + Type + Sort */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          {/* Source Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">
              Fuente
            </label>
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              {sources.map(source => (
                <option key={source} value={source}>
                  {source === 'all' ? 'Todas las fuentes' : source}
                </option>
              ))}
            </select>
          </div>

          {/* Type Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">
              Tipo
            </label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as TypeFilter)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              {types.map(t => (
                <option key={t.key} value={t.key}>{t.label}</option>
              ))}
            </select>
          </div>

          {/* Sort */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">
              Ordenar por
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              <option value="date_desc">Más recientes primero</option>
              <option value="date_asc">Más antiguos primero</option>
              <option value="source">Por fuente (A-Z)</option>
            </select>
          </div>
        </div>

        {/* Row 2: Toggle + Quick Filters */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Latest Only Toggle */}
          <button
            onClick={() => setLatestOnly(!latestOnly)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              latestOnly
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-gray-800/50 text-gray-400 border border-gray-700/50 hover:text-gray-200 hover:border-gray-600'
            }`}
          >
            <svg className={`w-3.5 h-3.5 ${latestOnly ? 'text-emerald-400' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Solo última publicación por fuente
          </button>

          {/* Quick source buttons */}
          <div className="hidden md:flex items-center gap-1.5 ml-auto">
            <span className="text-xs text-gray-500 mr-1">Filtro rápido:</span>
            {sources.slice(1).map(source => (
              <button
                key={source}
                onClick={() => setSourceFilter(sourceFilter === source ? 'all' : source)}
                className={`px-2 py-1 rounded text-xs transition-all ${
                  sourceFilter === source
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    : 'bg-gray-800/30 text-gray-500 border border-gray-700/30 hover:text-gray-300'
                }`}
              >
                {source}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results count */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">
          {filteredPublications.length} {filteredPublications.length === 1 ? 'publicación' : 'publicaciones'}
          {latestOnly && ' (última por fuente)'}
        </p>
        {(sourceFilter !== 'all' || typeFilter !== 'all' || latestOnly) && (
          <button
            onClick={() => {
              setSourceFilter('all');
              setTypeFilter('all');
              setLatestOnly(false);
              setSortBy('date_desc');
            }}
            className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            Limpiar filtros
          </button>
        )}
      </div>

      {isOffline && <OfflineBanner />}
      {error && <ApiError message={error} onRetry={reload} />}

      {loading && !publications && (
        <div className="space-y-3">
          {Array.from({ length: 4 }, (_, i) => (
            <div key={i} className="card h-28 animate-pulse bg-gray-900/50" />
          ))}
        </div>
      )}

      {/* Publications List */}
      <div className="space-y-3">
        {filteredPublications.map((pub: Publication) => (
          <PublicationItem key={pub.id} publication={pub} />
        ))}
      </div>

      {publications && filteredPublications.length === 0 && (
        <div className="text-center py-12 bg-gray-900/30 rounded-xl border border-gray-800">
          <svg className="w-12 h-12 text-gray-700 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-gray-500">No hay publicaciones con los filtros seleccionados.</p>
          <button
            onClick={() => {
              setSourceFilter('all');
              setTypeFilter('all');
              setLatestOnly(false);
            }}
            className="mt-3 text-sm text-blue-400 hover:text-blue-300"
          >
            Limpiar filtros
          </button>
        </div>
      )}
    </div>
  );
}

function PublicationItem({ publication }: { publication: Publication }) {
  return (
    <a
      href={publication.url}
      target="_blank"
      rel="noopener noreferrer"
      className="card block group hover:border-blue-500/30"
    >
      <div className="flex items-start gap-4">
        <div className="text-2xl flex-shrink-0 mt-1">
          {getTypeIcon(publication.type)}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4 mb-2">
            <h3 className="text-sm font-semibold text-white group-hover:text-blue-300 transition-colors leading-snug">
              {publication.title}
            </h3>
            <span className="text-xs text-gray-500 flex-shrink-0 mt-0.5">
              {getRelativeTime(publication.date)}
            </span>
          </div>
          
          <p className="text-sm text-gray-400 mb-3 line-clamp-2">
            {publication.description}
          </p>
          
          <div className="flex items-center gap-3 flex-wrap">
            <span className={`badge ${getSourceColor(publication.source)}`}>
              {publication.source}
            </span>
            <span className="badge badge-blue opacity-70">
              {getTypeLabel(publication.type)}
            </span>
            <span className="text-xs text-gray-500">
              {formatDate(publication.date)}
            </span>
            <span className="text-xs text-blue-400 group-hover:text-blue-300 flex items-center gap-1 ml-auto">
              Ver documento
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </span>
          </div>
        </div>
      </div>
    </a>
  );
}
