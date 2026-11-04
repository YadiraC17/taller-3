const configuredUrl = localStorage.getItem("fintrack_api_url");
const API_BASE = (configuredUrl || "http://127.0.0.1:5000/api").replace(/\/$/, "");
const TOKEN_KEY = "fintrack_access_token";

export const api = {
  get token() {
    return localStorage.getItem(TOKEN_KEY);
  },

  async request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (options.body && !(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }
    if (this.token) headers.set("Authorization", `Bearer ${this.token}`);

    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    } catch {
      throw new Error("No se pudo conectar con FINTRACK. Comprueba que la API esté activa.");
    }

    if (response.status === 204) return null;
    let body;
    try {
      body = await response.json();
    } catch {
      throw new Error("El servidor devolvió una respuesta no válida.");
    }
    if (!response.ok || body.success === false) {
      if (response.status === 401 && this.token) {
        localStorage.removeItem(TOKEN_KEY);
        window.dispatchEvent(new CustomEvent("fintrack:session-expired"));
      }
      throw new Error(body.message || "No se pudo completar la solicitud.");
    }
    return body.data;
  },

  async login(credentials) {
    const data = await this.request("/auth/login", { method: "POST", body: JSON.stringify(credentials) });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    return data.usuario;
  },

  async register(account) {
    return this.request("/auth/register", { method: "POST", body: JSON.stringify(account) });
  },

  clearSession() {
    localStorage.removeItem(TOKEN_KEY);
  },
};