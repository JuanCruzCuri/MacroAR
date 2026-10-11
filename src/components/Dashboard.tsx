import { useState } from 'react';
import { Indicator } from '../types';
import { mockIndicators } from '../data/mockData';
import IndicatorCard from './IndicatorCard';

const categories = [
  { key: 'all', label: 'Todos' },
  { key: 'inflacion', label: 'Inflación' },
  { key: 'actividad', label: 'Actividad' },
  { key: 'laboral', label: 'Laboral' },
  { key: 'comercio_exterior', label: 'Comercio Exterior' },
  { key: 'social', label: 'Social' },
  { key: 'expectativas', label: 'Expectativas' },
  { key: 'sector_publico', label: 'Sector Público' },
  { key: 'inmobiliario', label: 'Inmobiliario' },
];

export default function Dashboard() {
  const [filter, setFilter] = useState('all');

  const filteredIndicators = filter === 'all'
    ? mockIndicators
    : mockIndicators.filter(i => i.category === filter);

  return (
    <div>
      {/* Section Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">Indicadores Económicos</h2>
        <p className="text-gray-400 text-sm">
          Últimos valores publicados de las principales variables macroeconómicas de Argentina.
          Solo datos actuales — sin series históricas.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map(cat => (
          <button
            key={cat.key}
            onClick={() => setFilter(cat.key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filter === cat.key
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'bg-gray-800/50 text-gray-400 border border-gray-700/50 hover:text-gray-200 hover:border-gray-600'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Indicators Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredIndicators.map(indicator => (
          <IndicatorCard key={indicator.id} indicator={indicator} />
        ))}
      </div>

      {/* Info Banner */}
      <div className="mt-8 p-4 bg-gray-900/50 border border-gray-800 rounded-xl">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p className="text-sm text-gray-300">
              <span className="font-medium text-emerald-400">Datos verificados:</span> Los valores mostrados fueron obtenidos por scraping directo de las fuentes oficiales (INDEC, CIF-UTDT, DGEC-CABA, UCEMA).
              Se actualizan automáticamente todos los días a las 18:00 ART.
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Último scraping: 18 de Octubre 2026 · Los enlaces apuntan a los documentos PDF originales de cada fuente.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
