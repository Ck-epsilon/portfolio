// Author: Ck.epsilon & Chaos (AI Programming Assistant)
/** REST data provider for React-Admin, backed by api-starter FastAPI.
 *
 *  Expects standard paginated list format:
 *    GET /users?skip=0&limit=10&search=...  → [{ id, ... }, ...]
 *
 *  For a production deployment, replace with ra-data-simple-rest or a custom
 *  data provider that speaks your backend's exact pagination format.
 */

import { fetchUtils, DataProvider } from 'react-admin';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const httpClient = (url: string, options: fetchUtils.Options = {}) => {
  const token = localStorage.getItem('access_token');
  const headers = new Headers(options.headers as HeadersInit);
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return fetchUtils.fetchJson(url, { ...options, headers });
};

/** Generic record shape used by React-Admin data provider callbacks. */
interface Record {
  id: string | number;
  [key: string]: unknown;
}

export const dataProvider: DataProvider = {
  // ── List ──────────────────────────────────────────────────
  getList: async (resource, params) => {
    const { page, perPage } = params.pagination || { page: 1, perPage: 10 };
    const { field, order } = params.sort || { field: 'id', order: 'ASC' };
    const skip = (page - 1) * perPage;
    const search = params.filter?.q || '';

    const url = `${API_URL}/${resource}?skip=${skip}&limit=${perPage}` +
      (search ? `&search=${encodeURIComponent(search)}` : '') +
      (field ? `&sort=${encodeURIComponent(field)}&order=${encodeURIComponent(order)}` : '');

    const { json } = await httpClient(url);
    const data: Record[] = Array.isArray(json) ? json : json.items || [];

    // Client-side fallback: sort if backend didn't apply it
    if (field && !url.includes('sort=')) {
      data.sort((a, b) => {
        const av = a[field] as string | number;
        const bv = b[field] as string | number;
        if (av < bv) return order === 'ASC' ? -1 : 1;
        if (av > bv) return order === 'ASC' ? 1 : -1;
        return 0;
      });
    }

    return {
      data: data.map((item) => ({ ...item, id: item.id })),
      total: data.length < perPage ? skip + data.length : skip + perPage + 1,
    };
  },

  getOne: async (resource, params) => {
    const { json } = await httpClient(`${API_URL}/${resource}/${params.id}`);
    return { data: { ...json, id: json.id } };
  },

  getMany: async (resource, params) => {
    // Fetch individually since api-starter doesn't have bulk GET by IDs
    const results = await Promise.all(
      params.ids.map((id) =>
        httpClient(`${API_URL}/${resource}/${id}`).then(({ json }) => ({
          ...json,
          id: json.id,
        }))
      )
    );
    return { data: results };
  },

  getManyReference: async () => {
    return { data: [], total: 0 };
  },

  // ── Mutations ─────────────────────────────────────────────
  create: async (resource, params) => {
    const { json } = await httpClient(`${API_URL}/${resource}`, {
      method: 'POST',
      body: JSON.stringify(params.data),
    });
    return { data: { ...json, id: json.id } };
  },

  update: async (resource, params) => {
    const { json } = await httpClient(`${API_URL}/${resource}/${params.id}`, {
      method: 'PUT',
      body: JSON.stringify(params.data),
    });
    return { data: { ...json, id: json.id } };
  },

  updateMany: async () => {
    return { data: [] };
  },

  delete: async (resource, params) => {
    await httpClient(`${API_URL}/${resource}/${params.id}`, {
      method: 'DELETE',
    });
    return { data: params.previousData };
  },

  deleteMany: async () => {
    return { data: [] };
  },
};
