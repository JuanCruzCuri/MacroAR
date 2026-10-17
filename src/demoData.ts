// Datos de demo para cuando el backend no está disponible
export const DEMO_INDICATORS = [
  {
    id: "1",
    indicator_key: "ipc_mensual",
    name: "IPC Mensual",
    value: "2.7",
    unit: "%",
    period: "Agosto 2026",
    source: "INDEC",
    source_url: "https://www.indec.gob.ar/indec/web/Institucional-Indec-IPC",
    category: "inflacion",
    updated_at: "2026-09-26T18:00:00Z"
  },
  {
    id: "2",
    indicator_key: "emae_mom_sa",
    name: "EMAE (MoM Desestacionalizada)",
    value: "-0.3",
    unit: "%",
    period: "Julio 2026",
    source: "INDEC",
    source_url: "https://www.indec.gob.ar/indec/web/Institucional-Indec-Emae",
    category: "actividad",
    updated_at: "2026-09-26T18:00:00Z"
  },
  {
    id: "3",
    indicator_key: "ipi_manufacturero_mom_sa",
    name: "IPI Manufacturero (MoM SA)",
    value: "1.2",
    unit: "%",
    period: "Julio 2026",
    source: "INDEC",
    source_url: "https://www.indec.gob.ar/indec/web/Institucional-Indec-IPI",
    category: "actividad",
    updated_at: "2026-09-26T18:00:00Z"
  },
  {
    id: "4",
    indicator_key: "ipc_caba",
    name: "IPC CABA",
    value: "2.4",
    unit: "%",
    period: "Agosto 2026",
    source: "IPC CABA - DGEC",
    source_url: "https://www.estadisticaciudad.gob.ar/eyc/",
    category: "inflacion",
    updated_at: "2026-09-26T18:00:00Z"
  },
  {
    id: "5",
    indicator_key: "desocupacion",
    name: "Tasa de Desocupación",
    value: "6.8",
    unit: "%",
    period: "Q2 2026",
    source: "INDEC",
    source_url: "https://www.indec.gob.ar/indec/web/Institucional-Indec-TasaDesocupacion",
    category: "laboral",
    updated_at: "2026-09-26T18:00:00Z"
  },
  {
    id: "6",
    indicator_key: "salarios_mensual",
    name: "Índice de Salarios (Mensual)",
    value: "3.1",
    unit: "%",
    period: "Julio 2026",
    source: "INDEC",
    source_url: "https://www.indec.gob.ar/indec/web/Institucional-Indec-IS",
    category: "laboral",
    updated_at: "2026-09-26T18:00:00Z"
  },
  {
    id: "7",
    indicator_key: "balanza_comercial_yoy",
    name: "Balanza Comercial (YoY)",
    value: "15.2",
    unit: "%",
    period: "Agosto 2026",
    source: "INDEC",
    source_url: "https://www.indec.gob.ar/indec/web/Institucional-Indec-ComercioExterior",
    category: "sector_publico",
    updated_at: "2026-09-26T18:00:00Z"
  },
  {
    id: "8",
    indicator_key: "personal_apn_yoy",
    name: "Dotación Personal APN (YoY)",
    value: "-2.1",
    unit: "%",
    period: "Julio 2026",
    source: "INDEC",
    source_url: "https://www.indec.gob.ar/indec/web/Institucional-Indec-PersonalAPN",
    category: "sector_publico",
    updated_at: "2026-09-26T18:00:00Z"
  },
  {
    id: "9",
    indicator_key: "expectativas_inflacion",
    name: "Expectativas de Inflación",
    value: "2.8",
    unit: "%",
    period: "Septiembre 2026",
    source: "CIF-UTDT",
    source_url: "https://www.utdt.edu/ver_contenido.php?id=7",
    category: "expectativas",
    updated_at: "2026-09-26T18:00:00Z"
  },
  {
    id: "10",
    indicator_key: "m2_real",
    name: "M2 Real",
    value: "-1.8",
    unit: "%",
    period: "Agosto 2026",
    source: "UCEMA",
    source_url: "https://ucema.edu.ar/indices-y-bases-de-datos/m2-real",
    category: "inmobiliario",
    updated_at: "2026-09-26T18:00:00Z"
  }
];

export const DEMO_PUBLICATIONS = [
  {
    id: "1",
    title: "Índice de Precios al Consumidor - Agosto 2026",
    date: "2026-09-26",
    source: "INDEC",
    url: "https://www.indec.gob.ar/uploads/informesdeprensa/ipc_09_26A1BE2DC4CD.pdf",
    type: "informe",
    description: "El IPC registró un aumento de 2.7% en agosto 2026"
  },
  {
    id: "2",
    title: "EMAE - Julio 2026",
    date: "2026-09-26",
    source: "INDEC",
    url: "https://www.indec.gob.ar/uploads/informesdeprensa/emae_09_26.pdf",
    type: "informe",
    description: "El EMAE mostró una variación mensual desestacionalizada de -0.3%"
  },
  {
    id: "3",
    title: "Encuesta de Expectativas de Inflación - Septiembre 2026",
    date: "2026-09-25",
    source: "CIF-UTDT",
    url: "https://www.utdt.edu/download.php?fname=_177997411328279100.pdf",
    type: "reporte",
    description: "Mediana de expectativas de inflación a 12 meses: 2.8%"
  },
  {
    id: "4",
    title: "IPCBA - Agosto 2026",
    date: "2026-09-24",
    source: "IPC CABA - DGEC",
    url: "https://www.estadisticaciudad.gob.ar/eyc/publicaciones/ipc/",
    type: "informe",
    description: "El IPC de la Ciudad de Buenos Aires aumentó 2.4% en agosto"
  },
  {
    id: "5",
    title: "Informe M2 Real - Agosto 2026",
    date: "2026-09-20",
    source: "UCEMA",
    url: "https://ucema.edu.ar/indices-y-bases-de-datos/m2-real",
    type: "reporte",
    description: "Variación mensual del M2 Real: -1.8%"
  }
];
