// Author: Ck.epsilon & Chaos (AI Programming Assistant)
import { useState } from 'react';
import { ConfigProvider, theme, Layout, Menu, Button } from 'antd';
import {
  DashboardOutlined,
  TableOutlined,
  SettingOutlined,
  MoonOutlined,
  SunOutlined,
} from '@ant-design/icons';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import DashboardPage from './components/Dashboard';
import DataTablePage from './components/DataTable';

const { Sider, Content, Header } = Layout;

export default function App() {
  const [isDark, setIsDark] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '/table', icon: <TableOutlined />, label: 'Data Table' },
    { key: '/settings', icon: <SettingOutlined />, label: 'Settings' },
  ];

  return (
    <ConfigProvider
      theme={{
        algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: { colorPrimary: '#1677ff', borderRadius: 6 },
      }}
    >
      <Layout style={{ minHeight: '100vh' }}>
        <Sider breakpoint="lg" collapsedWidth="0">
          <div style={{
            height: 48, margin: 16, color: '#fff',
            fontSize: 18, fontWeight: 700, textAlign: 'center',
            lineHeight: '48px',
          }}>
            {isDark ? '🌙' : '☀️'} Admin
          </div>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
          />
        </Sider>
        <Layout>
          <Header style={{
            padding: '0 24px', display: 'flex',
            justifyContent: 'flex-end', alignItems: 'center',
            background: isDark ? '#141414' : '#fff',
          }}>
            <Button
              icon={isDark ? <SunOutlined /> : <MoonOutlined />}
              onClick={() => setIsDark(!isDark)}
              type="text"
            />
          </Header>
          <Content style={{ margin: 24 }}>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/table" element={<DataTablePage />} />
              <Route path="/settings" element={<SettingsPlaceholder />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

function SettingsPlaceholder() {
  return <h2>Settings — TBD</h2>;
}
