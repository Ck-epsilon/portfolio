# Fiverr Gig #3: Admin Dashboard (React + Ant Design)

> **Author:** Ck.epsilon
> **Stack:** React 18 · TypeScript · Vite · Ant Design 5 · Recharts · Docker
> **Portfolio:** [github.com/ck-epsilon](https://github.com/ck-epsilon) *(live previews available on request — portfolio growing weekly)*
> **Live preview included** — every order ships with a `preview.html` so you can see it before deployment.

## Gig 基本信息

| 字段 | 内容 |
|------|------|
| **Title** | Build a modern admin dashboard with React + Ant Design — pixel-perfect, fast delivery |
| **Category** | Programming & Tech → Software Development → Web Programming |
| **Service Type** | Frontend Development |
| **Price Tiers** | Basic $100 / Standard $200 / Premium $500 |
| **Delivery Time** | 3 / 5 / 10 days |

## Gig Description

**I'll build your admin panel, internal tool, or data dashboard — pixel-perfect and ready to connect to your API.**

Whether you need a customer management panel, an analytics dashboard, or an internal tool for your team — I deliver clean, responsive React frontends with Ant Design that look professional and work fast. Every dashboard ships with a live `preview.html` so you can see it working before deployment. Connects to your existing API or comes with mock data for demo.

**What you get:**
- Modern React (Vite + TypeScript + Hooks)
- Ant Design 5 UI components — clean, professional, battle-tested
- Responsive design — looks good on desktop, tablet, and mobile
- API integration (REST, with loading/error/empty states)
- Data tables with sorting, filtering, pagination, export
- Charts (Recharts — line, bar, pie)
- Dark mode toggle (light/dark/system)
- Live preview page — see your dashboard before deployment
- README with run + deploy instructions

**Why a custom dashboard instead of Retool / Budibase / no-code tools?**
- **You own the code** — Retool's Free plan works for ≤5 users, but locks you into their platform. Team plan starts at $10/builder/month + $5/internal user/month. At 5 builders that's $600/year, and you still don't own the source. Here: pay once, own everything.
- **Full customization** — no-code tools limit you to their component library. I build exactly what you need.
- **Self-hosted** — deploy on your own server. Your data stays yours. No vendor decides when to change pricing or sunset features.

**What you need to provide:**
- Page requirements (what screens you need, what data to show)
- API endpoints if integrating with your backend (Swagger/Postman doc preferred)
- Branding assets (logo, colors) if needed — or I'll use a clean default

---

## Price Tiers

### Basic ($100) — 3 Days · ⭐ Quick Dashboard
- Single-page dashboard (e.g., "Sales Overview")
- 2-3 data tables or KPI cards
- 1 chart (line, bar, or pie)
- Mock data included
- Responsive layout
- Light + dark mode
- Live preview page

### Standard ($200) — 5 Days · 🔥 Full Admin Panel
- Multi-page app with sidebar navigation
- 2-4 functional pages (Dashboard, DataTable, Users, Settings)
- Interactive data tables (sort, filter, search, paginate, export)
- 2-4 charts with data from your API or mock
- Form pages (create/edit with validation)
- Real API integration (you provide endpoints)

### Premium ($500) — 10 Days · 🚀 Enterprise-Ready
- Full admin panel: 4-6 pages
- Advanced data tables (export to CSV/Excel, column picker)
- Dashboard with drill-down analytics
- Real-time updates (WebSocket or polling)
- Notification system (toast alerts)
- Custom theme and branding (your logo + colors)
- Docker deployment
- Automated tests (Vitest)
- CI/CD pipeline (GitHub Actions)
- Deployment guide

---

## FAQ

**Q: Can you integrate with my existing backend?**
A: Yes. Just provide the API documentation (Swagger, Postman, or a written spec). I handle the rest.

**Q: What UI framework do you use?**
A: Default is Ant Design 5 — production-tested by Alibaba (Fortune 500), used by thousands of enterprises worldwide. Other frameworks (MUI, Chakra, Tailwind) available on request.

**Q: Will it work on mobile?**
A: Yes. Ant Design components are responsive by default. I test on desktop (1920px), tablet (768px), and mobile (375px) viewports.

**Q: Can I host this on my own server?**
A: Absolutely. It's a standard React app built with Vite. Deploy to Vercel, Netlify, AWS S3, Nginx, or any static hosting. I include a deployment guide.

**Q: What happens after delivery?**
A: You get the full source code + git history. Each tier includes 2 rounds of revisions. Post-delivery support: 7 days for bugs. Ongoing maintenance available on retainer.

**Q: Do you provide the source code?**
A: Yes — full source, git history, and setup instructions. No black boxes.

**Q: Can you add custom pages beyond the package?**
A: Absolutely. Message me with your requirements and I'll scope it.

---

## Code Template (Deliverable Preview)

```
admin-dashboard/
├── src/
│   ├── main.tsx               # Entry point
│   ├── App.tsx                # Root with sidebar layout + dark mode
│   ├── components/
│   │   ├── Dashboard.tsx      # KPI cards + charts
│   │   └── DataTable.tsx      # Searchable, sortable table
│   └── styles/
│       └── index.css          # Dark/light theme variables
├── screenshots/
│   └── dashboard.png
├── package.json
├── vite.config.ts
├── tsconfig.json
├── preview.html               # Live demo preview
└── README.md
```

**Sample `DataTable.tsx` (React + Ant Design):**
```tsx
import { Table, Input, Space } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useState, useMemo } from 'react';

interface DataTableProps<T> {
  data: T[];
  columns: any[];
  searchKeys?: string[];
  rowKey?: string;
}

export function DataTable<T extends Record<string, any>>({
  data, columns, searchKeys, rowKey = 'id'
}: DataTableProps<T>) {
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!search) return data;
    const keys = searchKeys || Object.keys(data[0] || {});
    return data.filter(row =>
      keys.some(k => String(row[k] || '').toLowerCase().includes(search.toLowerCase()))
    );
  }, [data, search, searchKeys]);

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Input
        prefix={<SearchOutlined />}
        placeholder="Search..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{ width: 280 }}
        allowClear
      />
      <Table
        dataSource={filtered}
        columns={columns}
        rowKey={rowKey}
        pagination={{ pageSize: 10, showSizeChanger: true }}
        scroll={{ x: true }}
      />
    </Space>
  );
}