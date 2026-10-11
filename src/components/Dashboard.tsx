import { useState } from 'react';
import { Indicator } from '../types';
import { mockIndicators } from '../data/mockData';
import IndicatorCard from './IndicatorCard';

const categories = [
  { key: 'all', label: 'Todos' },
  { key: 'inflacion', label: 'Inflación' },
  { key: 'actividad', label: 'Actividad' },
  { key: 'laboral', label: 'Laboral' },
  { key: 'cambiario', label: 'Cambiario' },
  { key: 'financiero', label: 'Financiero' },
  { key: 'monetario', label: 'Monetario' },
  { key: 'fiscal', label: 'Fiscal' },
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
          <svg className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p className="text-sm text-gray-300">
              <span className="font-medium text-blue-400">Nota:</span> Los datos se actualizan automáticamente cada viernes a las 18:00 ART.
              Las fuentes son públicas y oficiales. Los valores mostrados corresponden al último dato disponible al momento de la última ejecución.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
