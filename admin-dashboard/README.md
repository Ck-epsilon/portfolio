# Admin Dashboard — React + Ant Design

Modern admin panel with dark mode, data tables, and interactive charts. Built with React 18, TypeScript, Ant Design 5, and Recharts.

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Project Structure

```
admin-dashboard/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Layout, sidebar, routing, dark mode toggle
│   └── components/
│       ├── Dashboard.tsx     # KPI cards + line/bar charts
│       └── DataTable.tsx     # Searchable, filterable order table
├── public/
├── index.html
├── package.json
├── vite.config.ts
└── README.md
```

## Features

- **Dark / Light mode** — Single toggle, Ant Design theme-aware
- **Responsive sidebar** — Collapses on mobile, full on desktop
- **KPI dashboard** — Statistic cards with real-time-like data
- **Interactive charts** — Revenue trend line chart + traffic source bar chart (Recharts)
- **Data table** — Search by customer, filter by status, sort by column, pagination
- **Routing** — React Router with clean URL structure
- **TypeScript** — Full type safety

## Tech Stack

| Layer | Choice |
|-------|--------|
| Framework | React 18 + TypeScript |
| Build | Vite 5 |
| UI Library | Ant Design 5 |
| Icons | @ant-design/icons |
| Charts | Recharts |
| Routing | React Router 6 |
| Dates | dayjs |

## Customization

To adapt for your own project:

1. Replace mock data in `Dashboard.tsx` and `DataTable.tsx` with API calls
2. Add authentication via `App.tsx` route guard
3. Extend `SettingsPlaceholder` with real configuration forms
4. Add more pages in `src/components/` and register routes in `App.tsx`

## License

MIT — See repository LICENSE file.
