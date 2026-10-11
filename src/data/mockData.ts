import { Indicator, Publication } from '../types';

// Mock data simulating backend API response
export const mockIndicators: Indicator[] = [
  {
    id: '1',
    name: 'IPC Mensual',
    value: '3.2',
    unit: '%',
    period: 'Mayo 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'inflacion',
    updated_at: '2026-06-12T18:00:00-03:00'
  },
  {
    id: '2',
    name: 'IPC Interanual',
    value: '42.7',
    unit: '%',
    period: 'Mayo 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'inflacion',
    updated_at: '2026-06-12T18:00:00-03:00'
  },
  {
    id: '3',
    name: 'IPC CABA Mensual',
    value: '2.9',
    unit: '%',
    period: 'Mayo 2026',
    source: 'IPC CABA - DGEC',
    source_url: 'https://www.estadisticaciudad.gob.ar/',
    category: 'inflacion',
    updated_at: '2026-06-12T18:00:00-03:00'
  },
  {
    id: '4',
    name: 'EMAE (Actividad Económica)',
    value: '2.4',
    unit: '%',
    period: 'Marzo 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'actividad',
    updated_at: '2026-06-12T18:00:00-03:00'
  },
  {
    id: '5',
    name: 'Desocupación',
    value: '6.1',
    unit: '%',
    period: 'Q1 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'laboral',
    updated_at: '2026-06-12T18:00:00-03:00'
  },
  {
    id: '6',
    name: 'Brecha Cambiaria',
    value: '12.3',
    unit: '%',
    period: 'Junio 2026',
    source: 'CIF-UTDT',
    source_url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    category: 'cambiario',
    updated_at: '2026-06-12T18:00:00-03:00'
  },
  {
    id: '7',
    name: 'Riesgo País',
    value: '982',
    unit: 'pbs',
    period: 'Junio 2026',
    source: 'CIF-UTDT',
    source_url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    category: 'financiero',
    updated_at: '2026-06-12T18:00:00-03:00'
  },
  {
    id: '8',
    name: 'M2 Real (Base Dic/2016)',
    value: '91.5',
    unit: '% del PBI',
    period: 'Mayo 2026',
    source: 'UCEMA - Real M2 Report',
    source_url: 'https://www.ucema.edu.ar/',
    category: 'monetario',
    updated_at: '2026-06-12T18:00:00-03:00'
  },
  {
    id: '9',
    name: 'Salario Real (Índice)',
    value: '97.8',
    unit: '(Base 2016=100)',
    period: 'Abril 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'laboral',
    updated_at: '2026-06-12T18:00:00-03:00'
  },
  {
    id: '10',
    name: 'Resultado Fiscal (Sector Público)',
    value: '0.4',
    unit: '% PBI',
    period: 'Abril 2026',
    source: 'CIF-UTDT',
    source_url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    category: 'fiscal',
    updated_at: '2026-06-12T18:00:00-03:00'
  }
];

export const mockPublications: Publication[] = [
  {
    id: '1',
    title: 'Índice de Precios al Consumidor - Mayo 2026',
    date: '2026-06-12',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-IPC',
    type: 'informe',
    description: 'Variación mensual del IPC nacional. Rubros con mayor incremento: Alimentos y bebidas, Transporte.'
  },
  {
    id: '2',
    title: 'IPC Ciudad de Buenos Aires - Mayo 2026',
    date: '2026-06-10',
    source: 'DGEC - GCBA',
    url: 'https://www.estadisticaciudad.gob.ar/eyc/',
    type: 'informe',
    description: 'Informe mensual de precios al consumidor de la Ciudad Autónoma de Buenos Aires.'
  },
  {
    id: '3',
    title: 'Reporte Semanal CIF - Semana 24/2026',
    date: '2026-06-08',
    source: 'CIF-UTDT',
    url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    type: 'reporte',
    description: 'Análisis semanal de variables macroeconómicas: brecha cambiaria, riesgo país, y expectativas de mercado.'
  },
  {
    id: '4',
    title: 'EMAE - Marzo 2026: Estimador Mensual de Actividad Económica',
    date: '2026-06-05',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-EMAE',
    type: 'informe',
    description: 'Variación mensual y interanual del estimador mensual de actividad económica.'
  },
  {
    id: '5',
    title: 'Real M2 Report - Junio 2026',
    date: '2026-06-04',
    source: 'UCEMA',
    url: 'https://www.ucema.edu.ar/u/real-m2',
    type: 'reporte',
    description: 'Informe sobre la evolución del M2 real y su relación con el PBI. Análisis de demanda de dinero.'
  },
  {
    id: '6',
    title: 'Encuesta de Desocupación - 1er Trimestre 2026',
    date: '2026-05-29',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-TasaDesocupacion',
    type: 'informe',
    description: 'Tasa de desocupación nacional por aglomerados urbanos. Comparación interanual.'
  },
  {
    id: '7',
    title: 'Reporte Semanal CIF - Semana 23/2026',
    date: '2026-06-01',
    source: 'CIF-UTDT',
    url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    type: 'reporte',
    description: 'Seguimiento de variables clave: tipo de cambio, tasas de interés, y resultado fiscal.'
  },
  {
    id: '8',
    title: 'Índice de Salarios - Abril 2026',
    date: '2026-05-27',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-IS',
    type: 'informe',
    description: 'Variación del índice de salarios registrados. Evolución del salario real.'
  },
  {
    id: '9',
    title: 'Resultado del Sector Público Nacional - Abril 2026',
    date: '2026-05-24',
    source: 'CIF-UTDT',
    url: 'https://www.utdt.edu/centro-investigacion-finanzas',
    type: 'analisis',
    description: 'Análisis del resultado fiscal mensual. Desglose por componentes: ingresos, gastos y resultado primario.'
  },
  {
    id: '10',
    title: 'Balanza de Pagos - Q1 2026',
    date: '2026-05-21',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Institucional-Indec-BalanzaPagos',
    type: 'informe',
    description: 'Cuenta corriente, cuenta financiera y posición de inversión internacional.'
  }
];
