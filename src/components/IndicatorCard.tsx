import { Indicator } from '../types';

function getCategoryBadge(category: string): string {
  const map: Record<string, string> = {
    inflacion: 'badge-red',
    actividad: 'badge-blue',
    laboral: 'badge-green',
    comercio_exterior: 'badge-amber',
    social: 'badge-purple',
    expectativas: 'badge-purple',
    sector_publico: 'badge-amber',
    inmobiliario: 'badge-amber',
    cambiario: 'badge-amber',
    financiero: 'badge-purple',
    monetario: 'badge-blue',
    fiscal: 'badge-amber',
  };
  return map[category] || 'badge-blue';
}

function getCategoryLabel(category: string): string {
  const map: Record<string, string> = {
    inflacion: 'Inflación',
    actividad: 'Actividad',
    laboral: 'Laboral',
    comercio_exterior: 'Comercio Exterior',
    social: 'Social',
    expectativas: 'Expectativas',
    sector_publico: 'Sector Público',
    inmobiliario: 'Inmobiliario',
    cambiario: 'Cambiario',
    financiero: 'Financiero',
    monetario: 'Monetario',
    fiscal: 'Fiscal',
  };
  return map[category] || category;
}

function getSourceIcon(source: string): string {
  if (source.includes('INDEC')) return '🏛️';
  if (source.includes('CIF') || source.includes('UTDT')) return '🎓';
  if (source.includes('CABA') || source.includes('DGEC')) return '🏙️';
  if (source.includes('UCEMA')) return '📈';
  return '📊';
}

export default function IndicatorCard({ indicator }: { indicator: Indicator }) {
  return (
    <div className="card group">
      <div className="flex items-start justify-between mb-3">
        <span className={`badge ${getCategoryBadge(indicator.category)}`}>
          {getCategoryLabel(indicator.category)}
        </span>
        <span className="text-lg">{getSourceIcon(indicator.source)}</span>
      </div>
      
      <h3 className="text-sm font-medium text-gray-300 mb-2 group-hover:text-white transition-colors">
        {indicator.name}
      </h3>
      
      <div className="flex items-baseline gap-2 mb-3">
        <span className="text-3xl font-bold text-white tracking-tight">
          {indicator.value}
        </span>
        <span className="text-sm text-gray-400 font-medium">
          {indicator.unit}
        </span>
      </div>
      
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span className="bg-gray-800/50 px-2 py-0.5 rounded">
          {indicator.period}
        </span>
        <a
          href={indicator.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
        >
          {indicator.source}
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </div>
  );
}
