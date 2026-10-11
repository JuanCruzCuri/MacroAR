export default function ApiError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start justify-between gap-4">
      <div>
        <p className="text-sm font-medium text-red-400">No se pudieron cargar los datos</p>
        <p className="text-xs text-gray-400 mt-1">
          {message}. Si el servidor estaba inactivo puede tardar hasta un minuto en responder.
        </p>
      </div>
      <button
        onClick={onRetry}
        className="px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-800 text-gray-200 border border-gray-700 hover:border-gray-500 flex-shrink-0"
      >
        Reintentar
      </button>
    </div>
  );
}
