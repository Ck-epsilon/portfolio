// Author: Ck.epsilon & Chaos (AI Programming Assistant)
/** JWT auth provider for React-Admin.
 *
 *  Connects to api-starter FastAPI backend.
 *  Endpoints expected (can override via env VITE_API_URL):
 *    POST /auth/login     → { access_token, refresh_token, token_type }
 *    POST /auth/refresh   → { access_token }
 *    GET  /auth/me        → { id, username, email, role: { name, permissions } }
 */

import { AuthProvider, HttpError } from 'react-admin';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const authProvider: AuthProvider = {
  async login({ username, password }) {
    const resp = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new HttpError(err.detail || 'Login failed', resp.status);
    }
    const data = await resp.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token || '');
  },

  async logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  async checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) throw new HttpError('Not authenticated', 401);
  },

  async checkError(error) {
    const status = error.status;
    if (status === 401) {
      // Try refresh token
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const resp = await fetch(`${API_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refresh }),
          });
          if (resp.ok) {
            const data = await resp.json();
            localStorage.setItem('access_token', data.access_token);
            return;
          }
        } catch {}
      }
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      throw error;
    }
  },

  async getIdentity() {
    const token = localStorage.getItem('access_token');
    if (!token) throw new HttpError('Not authenticated', 401);
    const resp = await fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!resp.ok) throw new HttpError('Failed to fetch identity', resp.status);
    const user = await resp.json();
    return {
      id: user.id,
      fullName: user.username,
      avatar: undefined,
    };
  },

  async getPermissions() {
    const token = localStorage.getItem('access_token');
    if (!token) return [];
    try {
      const resp = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resp.ok) {
        const user = await resp.json();
        return user.role?.permissions?.map((p: { name: string }) => p.name) || [];
      }
    } catch {}
    return [];
  },
};
