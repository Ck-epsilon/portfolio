# Admin Dashboard — React + Ant Design / 管理面板

[English](#english) | [中文](#中文)

---

## English

### Supported Environment

| Software | Required | Tested |
|----------|----------|--------|
| Node.js | 18+ | 24.15.0 ✅ |
| npm | 9+ | 11.12.1 ✅ |
| React | 18+ | 18.x ✅ |
| TypeScript | 5+ | ✅ |
| Ant Design | 5+ | ✅ |

### Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:3000.

### Project Structure

```
admin-dashboard/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Layout, sidebar, routing, dark mode
│   └── components/
│       ├── Dashboard.tsx     # KPI cards + line/bar charts
│       └── DataTable.tsx     # Searchable, filterable table
├── screenshots/              # Demo screenshots
├── package.json
├── vite.config.ts
└── README.md
```

### Features

- **Dark / Light mode** — Single toggle, Ant Design theme-aware
- **Responsive sidebar** — Collapses on mobile
- **KPI dashboard** — Revenue, users, orders with charts (Recharts)
- **Data table** — Search, filter, sort, paginate
- **TypeScript** — Full type safety
- **Routing** — React Router 6

### Screenshots

| Dashboard | Data Table |
|-----------|------------|
| ![Dashboard](./screenshots/dashboard.png) | ![Table](./screenshots/table.png) |

---

## 中文

### 支持环境

| 软件 | 要求版本 | 实测 |
|------|---------|------|
| Node.js | 18+ | 24.15.0 ✅ |
| npm | 9+ | 11.12.1 ✅ |
| React | 18+ | 18.x ✅ |
| TypeScript | 5+ | ✅ |
| Ant Design | 5+ | ✅ |

### 快速启动

```bash
npm install
npm run dev
```

访问 http://localhost:3000。

### 项目结构

```
admin-dashboard/
├── src/
│   ├── main.tsx              # 入口
│   ├── App.tsx               # 布局/侧边栏/路由/暗色模式
│   └── components/
│       ├── Dashboard.tsx     # KPI 卡片 + 折线/柱状图
│       └── DataTable.tsx     # 可搜索/筛选的订单表格
├── screenshots/              # 演示截图
├── package.json
├── vite.config.ts
└── README.md
```

### 功能

- **暗色/亮色模式** — 一键切换，Ant Design 主题联动
- **响应式侧边栏** — 移动端自动折叠
- **KPI 仪表盘** — 收入/用户/订单统计 + Recharts 图表
- **数据表格** — 客户搜索、状态筛选、字段排序、分页
- **TypeScript** — 全类型安全
- **路由** — React Router 6

### 技术栈

| 层级 | 选择 |
|------|------|
| 框架 | React 18 + TypeScript |
| 构建 | Vite 5 |
| UI库 | Ant Design 5 |
| 图标 | @ant-design/icons |
| 图表 | Recharts |
| 路由 | React Router 6 |
