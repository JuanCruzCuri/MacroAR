# 🇦🇷 MacroAR — Datos Macroeconómicos de Argentina

Aplicación web que centraliza información macroeconómica de Argentina mediante scraping automático de fuentes públicas.

## 📋 Fuentes Monitoreadas

| Fuente | Indicadores | URL |
|--------|------------|-----|
| **INDEC** | IPC, EMAE, Desocupación, Salarios | [indec.gob.ar](https://www.indec.gob.ar) |
| **CIF-UTDT** | Brecha cambiaria, Riesgo país, Resultado fiscal | [utdt.edu/cif](https://www.utdt.edu/centro-investigacion-finanzas) |
| **IPC CABA** | IPC Ciudad de Buenos Aires | [estadisticaciudad.gob.ar](https://www.estadisticaciudad.gob.ar) |
| **UCEMA** | Real M2 Report | [ucema.edu.ar](https://www.ucema.edu.ar) |

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Vercel)                     │
│              React + Vite + Tailwind CSS                 │
│                    Dark Mode UI                          │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (Render/Railway)               │
│                 FastAPI + APScheduler                    │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Scraper  │  │ Scraper  │  │ Scraper  │  │Scraper │ │
│  │  INDEC   │  │ CIF-UTDT │  │ IPC CABA │  │ UCEMA  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘ │
│       │              │              │             │      │
│       └──────────────┴──────┬───────┴─────────────┘      │
│                             │                            │
│                    ┌────────▼────────┐                   │
│                    │   PostgreSQL    │                   │
│                    │  (Supabase/     │                   │
│                    │     Neon)       │                   │
│                    └─────────────────┘                   │
│                                                          │
│  📅 APScheduler: Viernes 18:00 ART                      │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Ejecución Local

### Opción 1: Docker Compose (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/macroar.git
cd macroar

# Copiar variables de entorno
cp backend/.env.example backend/.env

# Levantar todos los servicios
docker-compose up -d

# Acceder a:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Opción 2: Manual (sin Docker)

#### Backend:
```bash
cd backend

# Crear virtualenv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
# Opción A: PostgreSQL local
createdb macroar
# Opción B: Usar Supabase/Neon (editar .env)

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu DATABASE_URL

# Iniciar servidor
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend:
```bash
# En la raíz del proyecto
npm install
npm run dev
# Acceder a http://localhost:5173
```

### Trigger Manual de Scraping:
```bash
curl -X POST http://localhost:8000/api/scrape
```

## 🌐 Deploy a Producción

### Frontend → Vercel

```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Deploy
vercel

# 3. Configurar variable de entorno en Vercel Dashboard:
#    VITE_API_URL = https://tu-backend.onrender.com
```

El archivo `vercel.json` ya está configurado para el routing SPA.

### Backend → Render

1. **Crear cuenta en [Render](https://render.com)**
2. **New → Web Service**
3. **Conectar repositorio GitHub**
4. **Configuración:**
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     DATABASE_URL=postgresql://user:pass@host:5432/dbname
     FRONTEND_URL=https://macroar.vercel.app
     SCRAPE_DAY_OF_WEEK=fri
     SCRAPE_HOUR=18
     SCRAPE_MINUTE=0
     SCRAPE_TIMEZONE=America/Argentina/Buenos_Aires
     ```

### Backend → Railway (Alternativa)

```bash
# 1. Instalar Railway CLI
npm i -g @railway/cli

# 2. Login y crear proyecto
railway login
railway init

# 3. Agregar PostgreSQL service
railway add
# Seleccionar: PostgreSQL

# 4. Deploy
cd backend
railway up

# 5. Configurar variables
railway variables set DATABASE_URL=$DATABASE_URL
railway variables set FRONTEND_URL=https://macroar.vercel.app
```

### Base de Datos → Supabase (Recomendado)

1. Crear proyecto en [Supabase](https://supabase.com)
2. Copiar la Connection String (Settings → Database)
3. Usar como `DATABASE_URL` en el backend

### Base de Datos → Neon (Alternativa)

1. Crear cuenta en [Neon](https://neon.tech)
2. Crear proyecto y copiar connection string
3. Usar como `DATABASE_URL`

## 📁 Estructura del Proyecto

```
macroar/
├── src/                          # Frontend React
│   ├── App.tsx                   # Componente principal (2 tabs)
│   ├── components/
│   │   ├── Dashboard.tsx         # Tab 1: Indicadores actuales
│   │   ├── Feed.tsx              # Tab 2: Feed de publicaciones
│   │   ├── Header.tsx            # Header con branding
│   │   ├── Footer.tsx            # Footer
│   │   └── IndicatorCard.tsx     # Card individual de indicador
│   ├── data/
│   │   └── mockData.ts           # Datos de ejemplo (demo)
│   ├── types.ts                  # TypeScript interfaces
│   ├── index.css                 # Tailwind + custom styles
│   └── main.tsx                  # Entry point
├── backend/                      # Backend FastAPI
│   ├── main.py                   # App FastAPI + CORS + endpoints
│   ├── models.py                 # SQLAlchemy models (snapshot + feed)
│   ├── database.py               # DB connection
│   ├── config.py                 # Settings/env vars
│   ├── scheduler.py              # APScheduler (Viernes 18:00)
│   ├── utils.py                  # Limpieza de datos
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── indec.py              # Scraper INDEC
│   │   ├── cif.py                # Scraper CIF-UTDT
│   │   ├── ipc_caba.py           # Scraper IPC CABA
│   │   └── real_m2.py            # Scraper UCEMA Real M2
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml            # Orquestación local
├── vercel.json                   # Config Vercel frontend
├── package.json
└── README.md
```

## 🗄️ Esquema de Base de Datos

### `indicators_snapshot`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | SERIAL PK | ID autoincremental |
| indicator_key | VARCHAR(100) UNIQUE | Key del indicador (ej: "ipc_mensual") |
| name | VARCHAR(200) | Nombre legible |
| value | FLOAT | Valor numérico limpio |
| value_raw | VARCHAR(100) | Valor original tal como fue extraído |
| unit | VARCHAR(50) | Unidad (%, $, pbs) |
| period | VARCHAR(100) | Período (ej: "Mayo 2025") |
| source | VARCHAR(100) | Fuente (INDEC, CIF-UTDT, etc.) |
| source_url | TEXT | URL de la fuente |
| category | VARCHAR(50) | Categoría (inflacion, actividad, etc.) |
| updated_at | TIMESTAMPTZ | Última actualización |

### `publications_feed`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | SERIAL PK | ID autoincremental |
| title | VARCHAR(500) | Título de la publicación |
| date | TIMESTAMPTZ | Fecha de publicación |
| source | VARCHAR(100) | Fuente |
| url | TEXT UNIQUE | URL al documento original |
| type | VARCHAR(50) | Tipo (informe, reporte, analisis) |
| description | TEXT | Descripción breve |
| created_at | TIMESTAMPTZ | Fecha de inserción |
| updated_at | TIMESTAMPTZ | Última actualización |

## 🔧 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Info de la API |
| GET | `/api/health` | Health check |
| GET | `/api/indicators` | Todos los indicadores (snapshot) |
| GET | `/api/indicators/{key}` | Indicador específico |
| GET | `/api/publications` | Feed de publicaciones |
| POST | `/api/scrape` | Trigger manual de scraping |

## 🔒 Seguridad y CORS

- CORS configurado para aceptar solo el dominio del frontend
- Variables sensibles en `.env` (no commitear)
- En producción, agregar autenticación al endpoint `/api/scrape`

## 📅 Automatización

El scraping se ejecuta automáticamente:
- **Frecuencia:** Cada viernes
- **Hora:** 18:00 ART (America/Argentina/Buenos_Aires)
- **Tolerancia:** 1 hora (misfire_grace_time)

## 🧹 Limpieza de Datos

El módulo `utils.py` incluye funciones robustas para:
- Parseo de formatos numéricos argentinos (punto=miles, coma=decimal)
- Manejo de símbolos ($, %, US$)
- Fechas en español ("Mayo 2025", "Q1 2025")
- Valores nulos (N/D, -, s/d)
- Separadores inconsistentes

## 📝 Licencia

MIT

---

**Nota:** Los datos son obtenidos de fuentes públicas. Esta aplicación es un proyecto de código abierto con fines informativos.
