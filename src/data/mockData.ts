import { Indicator, Publication } from '../types';

// ============================================================
// Datos REALES obtenidos por scraping el 2026
// Fuentes: INDEC, CIF-UTDT, IPC CABA (DGEC), UCEMA
// ============================================================

export const mockIndicators: Indicator[] = [
  // === INFLACIÓN ===
  {
    id: '1',
    name: 'IPC Mensual (Nacional)',
    value: '1.7',
    unit: '%',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipc_09_26A1BE2DC4CD.pdf',
    category: 'inflacion',
    updated_at: '2026-09-26T18:00:00-03:00'
  },
  {
    id: '2',
    name: 'IPC Acumulado 2026',
    value: '21.3',
    unit: '%',
    period: 'Ene–Ago 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/',
    category: 'inflacion',
    updated_at: '2026-09-26T18:00:00-03:00'
  },
  {
    id: '3',
    name: 'IPCBA Mensual',
    value: '1.8',
    unit: '%',
    period: 'Septiembre 2026',
    source: 'IPC CABA - DGEC',
    source_url: 'https://www.estadisticaciudad.gob.ar/eyc/publicaciones/ipcba-ciudad-de-buenos-aires-agosto-de-2026-2/',
    category: 'inflacion',
    updated_at: '2026-10-16T18:00:00-03:00'
  },
  {
    id: '4',
    name: 'IPIM (Precios Mayoristas)',
    value: '2.1',
    unit: '%',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/indec/web/Nivel3-Tema-3-5',
    category: 'inflacion',
    updated_at: '2026-09-26T18:00:00-03:00'
  },
  {
    id: '5',
    name: 'ICC (Costo de la Construcción)',
    value: '2.4',
    unit: '%',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/uploads/informesdeprensa/icc_09_26FEFC2E3F64.pdf',
    category: 'inflacion',
    updated_at: '2026-09-26T18:00:00-03:00'
  },

  // === ACTIVIDAD ===
  {
    id: '6',
    name: 'EMAE (Actividad Económica)',
    value: '-2.9',
    unit: '%',
    period: 'Julio 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/uploads/informesdeprensa/emae_09_26FE154D8FFE.pdf',
    category: 'actividad',
    updated_at: '2026-09-26T18:00:00-03:00'
  },
  {
    id: '7',
    name: 'IPI Manufacturero',
    value: '1.9',
    unit: '%',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipi_manufacturero_10_264B0CD91C87.pdf',
    category: 'actividad',
    updated_at: '2026-10-16T18:00:00-03:00'
  },
  {
    id: '8',
    name: 'IPI Minero',
    value: '8.4',
    unit: '%',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipi_minero_10_26AEDFED4AA8.pdf',
    category: 'actividad',
    updated_at: '2026-10-16T18:00:00-03:00'
  },
  {
    id: '9',
    name: 'ISAC (Actividad Construcción)',
    value: '-4.4',
    unit: '%',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/uploads/informesdeprensa/isac_10_2674E79F6A29.pdf',
    category: 'actividad',
    updated_at: '2026-10-16T18:00:00-03:00'
  },
  {
    id: '10',
    name: 'UCII (Capacidad Instalada Industria)',
    value: '58.2',
    unit: '%',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/indec/web/Nivel3-Tema-3-7',
    category: 'actividad',
    updated_at: '2026-09-30T18:00:00-03:00'
  },

  // === LABORAL ===
  {
    id: '11',
    name: 'Desocupación',
    value: '7.9',
    unit: '%',
    period: 'Q2 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/uploads/informesdeprensa/mercado_trabajo_eph_2trim26433FCBC5A8.pdf',
    category: 'laboral',
    updated_at: '2026-09-26T18:00:00-03:00'
  },
  {
    id: '12',
    name: 'Índice de Salarios (Mensual)',
    value: '2.8',
    unit: '%',
    period: 'Julio 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-61',
    category: 'laboral',
    updated_at: '2026-09-26T18:00:00-03:00'
  },
  {
    id: '13',
    name: 'Índice de Salarios (Interanual)',
    value: '36.2',
    unit: '%',
    period: 'Julio 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-61',
    category: 'laboral',
    updated_at: '2026-09-26T18:00:00-03:00'
  },

  // === COMERCIO EXTERIOR ===
  {
    id: '14',
    name: 'Exportaciones de Bienes',
    value: '8883',
    unit: 'USD millones',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-2-40',
    category: 'comercio_exterior',
    updated_at: '2026-09-26T18:00:00-03:00'
  },
  {
    id: '15',
    name: 'Importaciones de Bienes',
    value: '6696',
    unit: 'USD millones',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-2-40',
    category: 'comercio_exterior',
    updated_at: '2026-09-26T18:00:00-03:00'
  },

  // === SOCIAL ===
  {
    id: '16',
    name: 'Pobreza (% Personas)',
    value: '32.3',
    unit: '%',
    period: 'S1 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/uploads/informesdeprensa/eph_pobreza_09_2670733F4C4D.pdf',
    category: 'social',
    updated_at: '2026-09-24T18:00:00-03:00'
  },
  {
    id: '17',
    name: 'Pobreza (% Hogares)',
    value: '24.4',
    unit: '%',
    period: 'S1 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/indec/web/Nivel3-Tema-4-46',
    category: 'social',
    updated_at: '2026-09-24T18:00:00-03:00'
  },
  {
    id: '18',
    name: 'Indigencia (% Personas)',
    value: '7.5',
    unit: '%',
    period: 'S1 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/uploads/informesdeprensa/eph_pobreza_09_2670733F4C4D.pdf',
    category: 'social',
    updated_at: '2026-09-24T18:00:00-03:00'
  },

  // === SECTOR PÚBLICO ===
  {
    id: '19',
    name: 'Dotación Personal APN',
    value: '269025',
    unit: 'personas',
    period: 'Agosto 2026',
    source: 'INDEC',
    source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-10-102',
    category: 'sector_publico',
    updated_at: '2026-09-30T18:00:00-03:00'
  },

  // === EXPECTATIVAS (CIF-UTDT) ===
  {
    id: '20',
    name: 'Expectativas de Inflación',
    value: '29.8',
    unit: '%',
    period: 'Septiembre 2026',
    source: 'CIF-UTDT',
    source_url: 'https://www.utdt.edu/ver_contenido.php?id_contenido=27163&id_item_menu=44653',
    category: 'expectativas',
    updated_at: '2026-09-30T18:00:00-03:00'
  },
  {
    id: '21',
    name: 'Índice Confianza del Consumidor',
    value: '2.4',
    unit: '%',
    period: 'Septiembre 2026',
    source: 'CIF-UTDT',
    source_url: 'https://www.utdt.edu/ver_contenido.php?id_contenido=27167&id_item_menu=44665',
    category: 'expectativas',
    updated_at: '2026-09-30T18:00:00-03:00'
  },
  {
    id: '22',
    name: 'Índice Líder (CIF)',
    value: '-0.27',
    unit: '%',
    period: 'Agosto 2026',
    source: 'CIF-UTDT',
    source_url: 'https://www.utdt.edu/ver_contenido.php?id_contenido=3146&id_item_menu=6227',
    category: 'actividad',
    updated_at: '2026-09-26T18:00:00-03:00'
  },

  // === INMOBILIARIO (UCEMA) ===
  {
    id: '23',
    name: 'M2 Real — Índice M² CABA',
    value: '0.16',
    unit: '%',
    period: 'Julio 2026',
    source: 'UCEMA',
    source_url: 'https://ucema.edu.ar/indices-y-bases-de-datos/m2-072026',
    category: 'inmobiliario',
    updated_at: '2026-08-16T18:00:00-03:00'
  },
  {
    id: '24',
    name: 'IPCBA Interanual',
    value: '32.9',
    unit: '%',
    period: 'Septiembre 2026',
    source: 'IPC CABA - DGEC',
    source_url: 'https://www.estadisticaciudad.gob.ar/eyc/',
    category: 'inflacion',
    updated_at: '2026-10-16T18:00:00-03:00'
  }
];

export const mockPublications: Publication[] = [
  {
    id: '1',
    title: 'IPCBA — Ciudad de Buenos Aires. Septiembre 2026',
    date: '2026-10-16',
    source: 'DGEC - GCBA',
    url: 'https://www.estadisticaciudad.gob.ar/eyc/buscador-publicaciones/',
    type: 'informe',
    description: 'Variación mensual 1,8%. Variación interanual 32,9%. Acumulado 2026: 32,9%.'
  },
  {
    id: '2',
    title: 'IPI Manufacturero — Agosto 2026',
    date: '2026-10-16',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipi_manufacturero_10_264B0CD91C87.pdf',
    type: 'informe',
    description: 'El índice de producción industrial manufacturero subió 1,9% en la serie desestacionalizada respecto al mes anterior. Cayó 3,2% interanual.'
  },
  {
    id: '3',
    title: 'IPI Minero — Agosto 2026',
    date: '2026-10-16',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipi_minero_10_26AEDFED4AA8.pdf',
    type: 'informe',
    description: 'El índice de producción industrial minero subió 8,4% respecto a igual mes de 2025. Acumulado enero-agosto 2026: +7,9%.'
  },
  {
    id: '4',
    title: 'Actividad de la Construcción (ISAC) — Agosto 2026',
    date: '2026-10-16',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/uploads/informesdeprensa/isac_10_2674E79F6A29.pdf',
    type: 'informe',
    description: 'El indicador sintético de la actividad de la construcción bajó 4,4% respecto a igual mes de 2025. Acumulado del año: +0,8%.'
  },
  {
    id: '5',
    title: 'Encuesta de Expectativas de Inflación — Septiembre 2026',
    date: '2026-09-30',
    source: 'CIF-UTDT',
    url: 'https://www.utdt.edu/download.php?fname=_177997411328279100.pdf',
    type: 'reporte',
    description: 'La mediana de las expectativas de inflación a 12 meses se ubicó en 29,8%.'
  },
  {
    id: '6',
    title: 'Índice de Confianza del Consumidor — Septiembre 2026',
    date: '2026-09-30',
    source: 'CIF-UTDT',
    url: 'https://www.utdt.edu/download.php?fname=_177937096786519200.pdf',
    type: 'reporte',
    description: 'El ICC subió +2,4% en septiembre respecto al mes anterior.'
  },
  {
    id: '7',
    title: 'Incidencia de la Pobreza — Primer Semestre 2026',
    date: '2026-09-24',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/uploads/informesdeprensa/eph_pobreza_09_2670733F4C4D.pdf',
    type: 'informe',
    description: 'La pobreza alcanzó al 32,3% de las personas (15 millones) y al 24,4% de los hogares. Indigencia: 7,5% de las personas.'
  },
  {
    id: '8',
    title: 'Índice de Precios al Consumidor — Agosto 2026',
    date: '2026-09-26',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipc_09_26A1BE2DC4CD.pdf',
    type: 'informe',
    description: 'El nivel general del IPC registró un alza mensual de 1,7% en agosto de 2026. Acumulado en el año: 21,3%.'
  },
  {
    id: '9',
    title: 'EMAE — Estimador Mensual de Actividad Económica. Julio 2026',
    date: '2026-09-26',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/uploads/informesdeprensa/emae_09_26FE154D8FFE.pdf',
    type: 'informe',
    description: 'El EMAE registró una variación de -2,9% en julio de 2026 respecto a igual mes del año anterior.'
  },
  {
    id: '10',
    title: 'Índice Líder — Agosto 2026: cae 0,27%',
    date: '2026-09-26',
    source: 'CIF-UTDT',
    url: 'https://www.utdt.edu/download.php?fname=_177928278524409400.pdf',
    type: 'reporte',
    description: 'El Índice Líder elaborado por el CIF cayó 0,27% en agosto de 2026. Probabilidad de recesión en 81%.'
  },
  {
    id: '11',
    title: 'Índice de Salarios — Julio 2026',
    date: '2026-09-26',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-61',
    type: 'informe',
    description: 'El índice de salarios se incrementó 2,8% mensual y 36,2% interanual. Acumula una suba de 21,8% respecto a diciembre de 2025.'
  },
  {
    id: '12',
    title: 'Índice del Costo de la Construcción (ICC) — Agosto 2026',
    date: '2026-09-26',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/uploads/informesdeprensa/icc_09_26FEFC2E3F64.pdf',
    type: 'informe',
    description: 'El nivel general del ICC en el Gran Buenos Aires correspondiente a agosto de 2026 registra una suba de 2,4%.'
  },
  {
    id: '13',
    title: 'Intercambio Comercial Argentino — Agosto 2026',
    date: '2026-09-26',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-2-40',
    type: 'informe',
    description: 'Exportaciones: USD 8.883 millones. Importaciones: USD 6.696 millones. Superávit comercial: USD 2.187 millones.'
  },
  {
    id: '14',
    title: 'Dotación de Personal de la APN — Agosto 2026',
    date: '2026-09-30',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-10-102',
    type: 'informe',
    description: 'Al 31 de agosto de 2026, la dotación de personal de la administración pública nacional fue de 269.025 personas.'
  },
  {
    id: '15',
    title: 'Encuesta de Desocupación — 2do Trimestre 2026',
    date: '2026-09-26',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/uploads/informesdeprensa/mercado_trabajo_eph_2trim26433FCBC5A8.pdf',
    type: 'informe',
    description: 'La tasa de desocupación se ubicó en 7,9% en el segundo trimestre de 2026.'
  },
  {
    id: '16',
    title: 'Informe M2 Real — Julio 2026',
    date: '2026-08-16',
    source: 'UCEMA',
    url: 'https://ucema.edu.ar/sites/default/files/2026-08/Informe_M2_Real_Julio_2026.pdf',
    type: 'reporte',
    description: 'Índice promedio CABA: 0,16%. Variación acumulada CABA: 3,30%. Índice de precios reales de departamentos en CABA.'
  },
  {
    id: '17',
    title: 'IPI Minero — Julio 2026',
    date: '2026-09-16',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipi_minero_09_26.pdf',
    type: 'informe',
    description: 'El índice de producción industrial minero registró variaciones positivas en la mayoría de los sectores.'
  },
  {
    id: '18',
    title: 'UCII — Capacidad Instalada en la Industria. Agosto 2026',
    date: '2026-09-30',
    source: 'INDEC',
    url: 'https://www.indec.gob.ar/indec/web/Nivel3-Tema-3-7',
    type: 'informe',
    description: 'La utilización de la capacidad instalada en la industria se ubicó en 58,2% en agosto de 2026.'
  }
];
