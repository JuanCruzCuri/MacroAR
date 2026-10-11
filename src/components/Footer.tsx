import { ScrapeStatus } from '../types';
import { formatDateTimeART } from '../api';

export default function Footer({ status }: { status: ScrapeStatus | null }) {
  const nextUpdate = formatDateTimeART(status?.next_scrape);

  return (
    <footer className="border-t border-gray-800 bg-gray-950 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-gray-500">
            Datos obtenidos de fuentes públicas: INDEC, CIF-UTDT, GCBA, UCEMA
          </p>
          {nextUpdate && (
            <p className="text-xs text-gray-600">
              Próxima actualización: {nextUpdate}
            </p>
          )}
        </div>
      </div>
    </footer>
  );
}
