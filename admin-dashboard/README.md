# Admin Dashboard — React-Admin + ε-style

Production admin panel built on React-Admin (26k+ stars), connected to api-starter FastAPI backend.

Stack: `React-Admin 5` · `MUI 6` · `Recharts` · `TypeScript` · `Vite`

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:5173. Login with api-starter credentials (default: admin/admin123).

Set `VITE_API_URL` in `.env` to point to your api-starter backend:
```
VITE_API_URL=http://localhost:8000
```

## Architecture

```
admin-dashboard/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # React-Admin <Admin> + resources + ε layout
│   ├── theme.ts              # ε-style theme (light + dark)
│   ├── authProvider.ts       # JWT auth → api-starter /auth/*
│   ├── dataProvider.ts       # REST data → api-starter /users, /items
│   └── resources/
│       ├── dashboard/        # KPI cards + Recharts bar chart
│       ├── users/            # List, Edit, Create, Show
│       └── items/            # List, Edit, Create, Show
├── package.json
└── vite.config.ts
```

## Features

| Feature | Implementation |
|---------|---------------|
| **Framework** | React-Admin 5 (not hand-written CRUD) |
| **Auth** | JWT login via api-starter `/auth/login` |
| **Data** | REST data provider → `/users`, `/items` |
| **CRUD** | Auto-generated List/Edit/Create/Show views |
| **Search** | `<TextInput source="q">` filter per resource |
| **Sort** | Click column headers in Datagrid |
| **Pagination** | Built-in, 10/25/50/100 per page |
| **Dark mode** | Toggle in AppBar (ε dark theme) |
| **Charts** | Recharts bar chart on Dashboard |
| **Permissions** | Role-aware: admin:access gates Edit button |
| **i18n** | React-Admin built-in (extendable to en/zh) |
| **TypeScript** | Full type safety |

## Why React-Admin over hand-written CRUD

| Hand-written | React-Admin |
|-------------|-------------|
| 200+ lines per List page (Table, sort, filter, pagination) | 10 lines: `<List><Datagrid>...` |
| 150+ lines per Edit form (validation, submit, error handling) | 8 lines: `<Edit><SimpleForm>...` |
| Custom auth logic (token refresh, 401 intercept) | authProvider: 4 functions |
| Custom API client (fetch + query string + error handling) | dataProvider: 7 functions |
| No undo/optimistic updates | Built-in |

## Customizing

### Add a new resource

1. Add to api-starter backend (FastAPI CRUD route)
2. Create `src/resources/products/index.tsx` with List/Edit/Create/Show
3. Add `<Resource name="products" ...>` to `App.tsx`

### Connect to a different backend

Edit `dataProvider.ts` — implement the 7 DataProvider methods for your API.

### Change theme

Edit `theme.ts` — the ε-style tokens are documented inline.

---

**Author:** Ck.epsilon & Chaos (AI Programming Assistant)
