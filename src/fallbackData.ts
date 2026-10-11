/**
 * Fallback data — datos reales obtenidos por scraping el 18 de octubre de 2026.
 * Se usan cuando el backend no está disponible (modo demo / offline).
 * Cuando el backend responde, estos datos se descartan y se usan los de la API.
 */
import { Indicator, Publication, ScrapeStatus } from './types';

export const FALLBACK_INDICATORS: Indicator[] = [
  // === INFLACIÓN ===
  { id: '1', indicator_key: 'ipc_mensual', name: 'IPC Mensual (Nacional)', value: '1,7', unit: '%', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31', category: 'inflacion', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '2', indicator_key: 'ipim_mensual', name: 'IPIM (Precios Mayoristas)', value: '2,1', unit: '%', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-32', category: 'inflacion', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '3', indicator_key: 'icc_construccion', name: 'ICC (Costo de la Construcción)', value: '2,4', unit: '%', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-33', category: 'inflacion', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '4', indicator_key: 'ipc_caba', name: 'IPCBA Mensual', value: '1,8', unit: '%', period: 'Septiembre 2026', source: 'IPC CABA - DGEC', source_url: 'https://www.estadisticaciudad.gob.ar/eyc/', category: 'inflacion', updated_at: '2026-10-18T18:00:00-03:00' },

  // === ACTIVIDAD (MoM Desestacionalizada) ===
  { id: '5', indicator_key: 'emae_mom_sa', name: 'EMAE (MoM Desestacionalizada)', value: '-2,9', unit: '%', period: 'Julio 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-9-48', category: 'actividad', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '6', indicator_key: 'ipi_manufacturero_mom_sa', name: 'IPI Manufacturero (MoM Desestacionalizada)', value: '1,9', unit: '%', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-6-14', category: 'actividad', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '7', indicator_key: 'ipi_minero_mom_sa', name: 'IPI Minero (MoM Desestacionalizada)', value: '1,9', unit: '%', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel3-Tema-3-7', category: 'actividad', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '8', indicator_key: 'isac_mom_sa', name: 'ISAC Construcción (MoM Desestacionalizada)', value: '0,4', unit: '%', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel3-Tema-3-3', category: 'actividad', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '9', indicator_key: 'ucii', name: 'UCII (Capacidad Instalada Industria)', value: '58,2', unit: '%', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-6-15', category: 'actividad', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '10', indicator_key: 'indice_lider', name: 'Índice Líder (CIF)', value: '-0,27', unit: '%', period: 'Agosto 2026', source: 'CIF-UTDT', source_url: 'https://www.utdt.edu/cif', category: 'actividad', updated_at: '2026-10-18T18:00:00-03:00' },

  // === COMERCIO EXTERIOR ===
  { id: '11', indicator_key: 'balanza_exportaciones', name: 'Exportaciones de Bienes', value: '8.883', unit: 'USD millones', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-2-40', category: 'comercio_exterior', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '12', indicator_key: 'balanza_importaciones', name: 'Importaciones de Bienes', value: '6.696', unit: 'USD millones', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-2-40', category: 'comercio_exterior', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '13', indicator_key: 'balanza_saldo', name: 'Saldo Comercial', value: '2.187', unit: 'USD millones', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-2-40', category: 'comercio_exterior', updated_at: '2026-10-18T18:00:00-03:00' },

  // === LABORAL ===
  { id: '14', indicator_key: 'desocupacion', name: 'Tasa de Desocupación', value: '7,9', unit: '%', period: 'Q2 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-58', category: 'laboral', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '15', indicator_key: 'salarios_mensual', name: 'Índice de Salarios (Mensual)', value: '2,8', unit: '%', period: 'Julio 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-61', category: 'laboral', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '16', indicator_key: 'salarios_interanual', name: 'Índice de Salarios (Interanual)', value: '36,2', unit: '%', period: 'Julio 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-61', category: 'laboral', updated_at: '2026-10-18T18:00:00-03:00' },

  // === SOCIAL ===
  { id: '17', indicator_key: 'pobreza_personas', name: 'Pobreza (% Personas)', value: '32,3', unit: '%', period: 'S1 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel3-Tema-4-46', category: 'social', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '18', indicator_key: 'pobreza_hogares', name: 'Pobreza (% Hogares)', value: '24,4', unit: '%', period: 'S1 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel3-Tema-4-46', category: 'social', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '19', indicator_key: 'indigencia', name: 'Indigencia (% Personas)', value: '7,5', unit: '%', period: 'S1 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel3-Tema-4-46', category: 'social', updated_at: '2026-10-18T18:00:00-03:00' },

  // === EXPECTATIVAS ===
  { id: '20', indicator_key: 'expectativas_inflacion', name: 'Expectativas de Inflación', value: '29,8', unit: '%', period: 'Septiembre 2026', source: 'CIF-UTDT', source_url: 'https://www.utdt.edu/cif', category: 'expectativas', updated_at: '2026-10-18T18:00:00-03:00' },
  { id: '21', indicator_key: 'confianza_consumidor', name: 'Índice Confianza del Consumidor', value: '2,4', unit: '%', period: 'Septiembre 2026', source: 'CIF-UTDT', source_url: 'https://www.utdt.edu/cif', category: 'expectativas', updated_at: '2026-10-18T18:00:00-03:00' },

  // === SECTOR PÚBLICO ===
  { id: '22', indicator_key: 'personal_apn_yoy', name: 'Dotación Personal APN (YoY)', value: '-5,8', unit: '%', period: 'Agosto 2026', source: 'INDEC', source_url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-10-102', category: 'sector_publico', updated_at: '2026-10-18T18:00:00-03:00' },

  // === INMOBILIARIO ===
  { id: '23', indicator_key: 'm2_real_indice', name: 'M2 Real — Índice M² CABA', value: '0,16', unit: '%', period: 'Julio 2026', source: 'UCEMA', source_url: 'https://ucema.edu.ar/indices-y-bases-de-datos', category: 'inmobiliario', updated_at: '2026-10-18T18:00:00-03:00' },
];

export const FALLBACK_PUBLICATIONS: Publication[] = [
  { id: '1', title: 'IPCBA — Ciudad de Buenos Aires. Septiembre 2026', date: '2026-10-16', source: 'DGEC - GCBA', url: 'https://www.estadisticaciudad.gob.ar/eyc/buscador-publicaciones/', type: 'informe', description: 'Variación mensual 1,8%. Variación interanual 32,9%. Acumulado 2026: 32,9%.' },
  { id: '2', title: 'IPI Manufacturero — Agosto 2026', date: '2026-10-16', source: 'INDEC', url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipi_manufacturero_10_264B0CD91C87.pdf', type: 'informe', description: 'El índice de producción industrial manufacturero subió 1,9% en la serie desestacionalizada respecto al mes anterior. Cayó 3,2% interanual.' },
  { id: '3', title: 'IPI Minero — Agosto 2026', date: '2026-10-16', source: 'INDEC', url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipi_minero_10_26AEDFED4AA8.pdf', type: 'informe', description: 'El índice de producción industrial minero subió 8,4% respecto a igual mes de 2025. En serie desestacionalizada, subió 1,9% frente a julio.' },
  { id: '4', title: 'Actividad de la Construcción (ISAC) — Agosto 2026', date: '2026-10-16', source: 'INDEC', url: 'https://www.indec.gob.ar/uploads/informesdeprensa/isac_10_2674E79F6A29.pdf', type: 'informe', description: 'El indicador sintético de la actividad de la construcción subió 0,4% desestacionalizado respecto al mes anterior. Cayó 4,4% interanual.' },
  { id: '5', title: 'Encuesta de Expectativas de Inflación — Septiembre 2026', date: '2026-09-30', source: 'CIF-UTDT', url: 'https://www.utdt.edu/cif', type: 'reporte', description: 'La mediana de las expectativas de inflación a 12 meses se ubicó en 29,8%.' },
  { id: '6', title: 'Índice de Confianza del Consumidor — Septiembre 2026', date: '2026-09-30', source: 'CIF-UTDT', url: 'https://www.utdt.edu/cif', type: 'reporte', description: 'El ICC subió +2,4% en septiembre respecto al mes anterior.' },
  { id: '7', title: 'Incidencia de la Pobreza — Primer Semestre 2026', date: '2026-09-24', source: 'INDEC', url: 'https://www.indec.gob.ar/uploads/informesdeprensa/eph_pobreza_09_2670733F4C4D.pdf', type: 'informe', description: 'La pobreza alcanzó al 32,3% de las personas y al 24,4% de los hogares. Indigencia: 7,5% de las personas.' },
  { id: '8', title: 'Índice de Precios al Consumidor — Agosto 2026', date: '2026-09-26', source: 'INDEC', url: 'https://www.indec.gob.ar/uploads/informesdeprensa/ipc_09_26A1BE2DC4CD.pdf', type: 'informe', description: 'El nivel general del IPC registró un alza mensual de 1,7% en agosto de 2026. Acumulado en el año: 21,3%.' },
  { id: '9', title: 'EMAE — Estimador Mensual de Actividad Económica. Julio 2026', date: '2026-09-26', source: 'INDEC', url: 'https://www.indec.gob.ar/uploads/informesdeprensa/emae_09_26FE154D8FFE.pdf', type: 'informe', description: 'El EMAE cayó 2,9% desestacionalizado respecto al mes anterior. Interanual: -1,4%.' },
  { id: '10', title: 'Índice Líder — Agosto 2026', date: '2026-09-26', source: 'CIF-UTDT', url: 'https://www.utdt.edu/cif', type: 'reporte', description: 'El Índice Líder elaborado por el CIF cayó 0,27% en agosto de 2026. Probabilidad de recesión en 81%.' },
  { id: '11', title: 'Índice de Salarios — Julio 2026', date: '2026-09-26', source: 'INDEC', url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-61', type: 'informe', description: 'El índice de salarios se incrementó 2,8% mensual y 36,2% interanual. Acumula una suba de 21,8% respecto a diciembre de 2025.' },
  { id: '12', title: 'Índice del Costo de la Construcción (ICC) — Agosto 2026', date: '2026-09-26', source: 'INDEC', url: 'https://www.indec.gob.ar/uploads/informesdeprensa/icc_09_26FEFC2E3F64.pdf', type: 'informe', description: 'El nivel general del ICC en el Gran Buenos Aires correspondiente a agosto de 2026 registra una suba de 2,4%.' },
  { id: '13', title: 'Intercambio Comercial Argentino — Agosto 2026', date: '2026-09-26', source: 'INDEC', url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-2-40', type: 'informe', description: 'Exportaciones: USD 8.883 millones (+12,4% i.a.). Importaciones: USD 6.696 millones (+3,6% i.a.). Superávit: USD 2.187 millones.' },
  { id: '14', title: 'Dotación de Personal de la APN — Agosto 2026', date: '2026-09-30', source: 'INDEC', url: 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-10-102', type: 'informe', description: 'Al 31 de agosto de 2026, la dotación fue de 269.025 personas; caída de 5,8% interanual (-16.669 personas).' },
  { id: '15', title: 'Encuesta de Desocupación — 2do Trimestre 2026', date: '2026-09-26', source: 'INDEC', url: 'https://www.indec.gob.ar/uploads/informesdeprensa/mercado_trabajo_eph_2trim26433FCBC5A8.pdf', type: 'informe', description: 'La tasa de desocupación se ubicó en 7,9% en el segundo trimestre de 2026.' },
  { id: '16', title: 'Informe M2 Real — Julio 2026', date: '2026-08-16', source: 'UCEMA', url: 'https://ucema.edu.ar/indices-y-bases-de-datos/m2-072026', type: 'reporte', description: 'Índice promedio CABA: 0,16%. Variación acumulada CABA: 3,30%. Índice de precios reales de departamentos en CABA.' },
];

export const FALLBACK_STATUS: ScrapeStatus = {
  last_scrape: '2026-10-18T21:00:00.000Z',  // 18:00 ART
  next_scrape: '2026-10-19T21:00:00.000Z',  // 19:00 ART
  timezone: 'America/Argentina/Buenos_Aires',
};
