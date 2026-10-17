export default function DemoBanner() {
  return (
    <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 mb-6">
      <div className="flex items-start gap-3">
        <svg className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-amber-400 mb-1">Modo Demo</h3>
          <p className="text-xs text-gray-400">
            Mostrando datos de ejemplo. Para ver datos en tiempo real, configurá el backend y la variable <code className="bg-gray-800 px-1.5 py-0.5 rounded text-amber-300">VITE_API_URL</code>.
          </p>
        </div>
      </div>
    </div>
  );
}
