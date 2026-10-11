import { Indicator, Publication } from '../types';

// Mock data simulating backend API response
export const mockIndicators: Indicator[] = [
  {
    id: '1',
    name: 'IPC Mensual',
    value: '4.1',
    unit: '%',
    period: 'Mayo 2025',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'inflacion',
    updated_at: '2025-06-13T18:00:00-03:00'
  },
  {
    id: '2',
    name: 'IPC Interanual',
    value: '112.3',
    unit: '%',
    period: 'Mayo 2025',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'inflacion',
    updated_at: '2025-06-13T18:00:00-03:00'
  },
  {
    id: '3',
    name: 'IPC CABA Mensual',
    value: '3.8',
    unit: '%',
    period: 'Mayo 2025',
    source: 'IPC CABA - DGEC',
    source_url: 'https://www.estadisticaciudad.gob.ar/',
    category: 'inflacion',
    updated_at: '2025-06-13T18:00:00-03:00'
  },
  {
    id: '4',
    name: 'EMAE (Actividad Económica)',
    value: '1.2',
    unit: '%',
    period: 'Marzo 2025',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'actividad',
    updated_at: '2025-06-13T18:00:00-03:00'
  },
  {
    id: '5',
    name: 'Desocupación',
    value: '7.4',
    unit: '%',
    period: 'Q1 2025',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'laboral',
    updated_at: '2025-06-13T18:00:00-03:00'
  },
  {
    id: '6',
    name: 'Brecha Cambiaria',
    value: '18.5',
    unit: '%',
    period: 'Junio 2025',
    source: 'CIF-UTDT',
    source_url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    category: 'cambiario',
    updated_at: '2025-06-13T18:00:00-03:00'
  },
  {
    id: '7',
    name: 'Riesgo País',
    value: '1487',
    unit: 'pbs',
    period: 'Junio 2025',
    source: 'CIF-UTDT',
    source_url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    category: 'financiero',
    updated_at: '2025-06-13T18:00:00-03:00'
  },
  {
    id: '8',
    name: 'M2 Real (Base Dic/2016)',
    value: '87.3',
    unit: '% del PBI',
    period: 'Mayo 2025',
    source: 'UCEMA - Real M2 Report',
    source_url: 'https://www.ucema.edu.ar/',
    category: 'monetario',
    updated_at: '2025-06-13T18:00:00-03:00'
  },
  {
    id: '9',
    name: 'Salario Real (Índice)',
    value: '92.1',
    unit: '(Base 2016=100)',
    period: 'Abril 2025',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'laboral',
    updated_at: '2025-06-13T18:00:00-03:00'
  },
  {
    id: '10',
    name: 'Resultado Fiscal (Sector Público)',
    value: '0.8',
    unit: '% PBI',
    period: 'Abril 2025',
    source: 'CIF-UTDT',
    source_url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    category: 'fiscal',
    updated_at: '2025-06-13T18:00:00-03:00'
  }
];

export const mockPublications: Publication[] = [
  {
    id: '1',
    title: 'Índice de Precios al Consumidor - Mayo 2025',
    date: '2025-06-13',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-IPC',
    type: 'informe',
    description: 'Variación mensual del IPC nacional. Rubros con mayor incremento: Alimentos y bebidas, Transporte.'
  },
  {
    id: '2',
    title: 'IPC Ciudad de Buenos Aires - Mayo 2025',
    date: '2025-06-11',
    source: 'DGEC - GCBA',
    url: 'https://www.estadisticaciudad.gob.ar/eyc/',
    type: 'informe',
    description: 'Informe mensual de precios al consumidor de la Ciudad Autónoma de Buenos Aires.'
  },
  {
    id: '3',
    title: 'Reporte Semanal CIF - Semana 23/2025',
    date: '2025-06-09',
    source: 'CIF-UTDT',
    url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    type: 'reporte',
    description: 'Análisis semanal de variables macroeconómicas: brecha cambiaria, riesgo país, y expectativas de mercado.'
  },
  {
    id: '4',
    title: 'EMAE - Marzo 2025: Estimador Mensual de Actividad Económica',
    date: '2025-06-06',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-EMAE',
    type: 'informe',
    description: 'Variación mensual y interanual del estimador mensual de actividad económica.'
  },
  {
    id: '5',
    title: 'Real M2 Report - Junio 2025',
    date: '2025-06-05',
    source: 'UCEMA',
    url: 'https://www.ucema.edu.ar/u/real-m2',
    type: 'reporte',
    description: 'Informe sobre la evolución del M2 real y su relación con el PBI. Análisis de demanda de dinero.'
  },
  {
    id: '6',
    title: 'Encuesta de Desocupación - 1er Trimestre 2025',
    date: '2025-05-30',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-TasaDesocupacion',
    type: 'informe',
    description: 'Tasa de desocupación nacional por aglomerados urbanos. Comparación interanual.'
  },
  {
    id: '7',
    title: 'Reporte Semanal CIF - Semana 22/2025',
    date: '2025-06-02',
    source: 'CIF-UTDT',
    url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    type: 'reporte',
    description: 'Seguimiento de variables clave: tipo de cambio, tasas de interés, y resultado fiscal.'
  },
  {
    id: '8',
    title: 'Índice de Salarios - Abril 2025',
    date: '2025-05-28',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-IS',
    type: 'informe',
    description: 'Variación del índice de salarios registrados. Evolución del salario real.'
  },
  {
    id: '9',
    title: 'Resultado del Sector Público Nacional - Abril 2025',
    date: '2025-05-25',
    source: 'CIF-UTDT',
    url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    type: 'analisis',
    description: 'Análisis del resultado fiscal mensual. Desglose por componentes: ingresos, gastos y resultado primario.'
  },
  {
    id: '10',
    title: 'Balanza de Pagos - Q1 2025',
    date: '2025-05-22',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-BalanzaPagos',
    type: 'informe',
    description: 'Cuenta corriente, cuenta financiera y posición de inversión internacional.'
  }
];
