/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** URL del backend FastAPI, p. ej. https://macroar-backend.onrender.com */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
