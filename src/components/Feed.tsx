import { useState } from 'react';
import { Publication } from '../types';
import { mockPublications } from '../data/mockData';

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

function formatDate(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
}

function getRelativeTime(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00');
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Hoy';
  if (diffDays === 1) return 'Ayer';
  if (diffDays < 7) return `Hace ${diffDays} días`;
  if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
  return `Hace ${Math.floor(diffDays / 30)} meses`;
}

export default function Feed() {
  const [sourceFilter, setSourceFilter] = useState('all');
  
  const sources = ['all', 'INDEC', 'CIF-UTDT', 'DGEC - GCBA', 'UCEMA'];
  
  const filteredPublications = sourceFilter === 'all'
    ? mockPublications
    : mockPublications.filter(p => p.source === sourceFilter);

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

      {/* Source Filters */}
      <div className="flex flex-wrap gap-2 mb-6">
        {sources.map(source => (
          <button
            key={source}
            onClick={() => setSourceFilter(source)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              sourceFilter === source
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'bg-gray-800/50 text-gray-400 border border-gray-700/50 hover:text-gray-200 hover:border-gray-600'
            }`}
          >
            {source === 'all' ? 'Todas las fuentes' : source}
          </button>
        ))}
      </div>

      {/* Publications List */}
      <div className="space-y-3">
        {filteredPublications.map((pub: Publication) => (
          <PublicationItem key={pub.id} publication={pub} />
        ))}
      </div>

      {filteredPublications.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No hay publicaciones para esta fuente.</p>
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
