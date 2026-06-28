// frontend/lib/api.ts
import { getAuthToken, setAuthToken, clearAuthToken } from './stores/authStore';
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (options.headers) {
    const extra = options.headers as Record<string, string>;
    Object.assign(headers, extra);
  }
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {

        const refreshRes = await fetch(`${API_BASE}/api/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (refreshRes.ok) {
          const { access_token, refresh_token } = await refreshRes.json();
          setAuthToken(access_token, refresh_token);
          const retryHeaders: Record<string, string> = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${access_token}`,
          };
          const retry = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: retryHeaders,
          });
          return retry;
        } else {
          clearAuthToken();
          throw new Error('Session expired');
        }
      } catch {
        clearAuthToken();
        throw new Error('Session expired');
      }
    } else {
      clearAuthToken();
      throw new Error('Not authenticated');
    }
  }
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response;
}
export async function apiGet<T>(endpoint: string): Promise<T> {
  const res = await fetchWithAuth(endpoint);
  return res.json();
}
export async function apiPost<T>(endpoint: string, data?: any): Promise<T> {
  console.log("📡 apiPost called with:", endpoint, data);
  const res = await fetchWithAuth(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
  const json = await res.json();
  console.log("📡 apiPost response:", json);
  return json;
}
export async function apiPatch<T>(endpoint: string, data?: any): Promise<T> {
  const res = await fetchWithAuth(endpoint, {
    method: 'PATCH',
    body: data ? JSON.stringify(data) : undefined,
  });
  return res.json();
}

export async function apiDelete<T>(endpoint: string): Promise<T> {
  const res = await fetchWithAuth(endpoint, { method: 'DELETE' });
  return res.json();
}
export async function apiUpload(endpoint: string, formData: FormData): Promise<any> {
  const token = getAuthToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    body: formData,
    headers,
  });
  if (res.status === 401) {
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}
