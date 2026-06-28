// Author: Ck.epsilon
import { useState } from 'react';
import { ConfigProvider, theme, Layout, Menu, Button } from 'antd';
import {
  DashboardOutlined,
  TableOutlined,
  FormOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  MoonOutlined,
  SunOutlined,
} from '@ant-design/icons';
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { useAuth } from './components/AuthContext';
import { useI18n } from './components/I18nContext';
import DashboardPage from './components/Dashboard';
import DataTablePage from './components/DataTable';
import FormPage from './components/FormPage';
import LoginPage from './components/LoginPage';
import ProfilePage from './components/ProfilePage';
import SettingsPage from './components/SettingsPage';

const { Sider, Content, Header } = Layout;

export default function App() {
  const { isAuthenticated, logout } = useAuth();
  const { t } = useI18n();
  const [isDark, setIsDark] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  if (!isAuthenticated) {
    return (
      <ConfigProvider
        theme={{
          algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
          token: { colorPrimary: '#1677ff', borderRadius: 6 },
        }}
      >
        <LoginPage />
      </ConfigProvider>
    );
  }

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: t('dashboard') },
    { key: '/table', icon: <TableOutlined />, label: t('dataTable') },
    { key: '/form', icon: <FormOutlined />, label: t('ordersCrud') },
    { key: '/profile', icon: <UserOutlined />, label: t('profile') },
    { key: '/settings', icon: <SettingOutlined />, label: t('settings') },
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
            <Button icon={isDark ? <SunOutlined /> : <MoonOutlined />} onClick={() => setIsDark(!isDark)} type="text" />
            <Button icon={<LogoutOutlined />} onClick={logout} type="text" style={{ marginLeft: 8 }} />
          </Header>
          <Content style={{ margin: 24 }}>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/table" element={<DataTablePage />} />
              <Route path="/form" element={<FormPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/settings" element={<SettingsPage isDark={isDark} toggleDark={() => setIsDark(!isDark)} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}
