/** Gateway base URL from Vite env (defaults to local Compose gateway). */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") ||
  "http://localhost:8000";
