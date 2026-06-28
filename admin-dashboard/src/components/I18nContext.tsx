// Author: Ck.epsilon & Chaos (AI Programming Assistant)
/** Lightweight i18n for Chinese/English switching. No external deps. */

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

const messages: Record<string, Record<string, string>> = {
  en: {
    login: 'Login',
    logout: 'Logout',
    email: 'Email',
    password: 'Password',
    loginTitle: 'Sign in to Dashboard',
    loginBtn: 'Sign In',
    loginError: 'Invalid email or password',
    settings: 'Settings',
    profile: 'Profile',
    dashboard: 'Dashboard',
    dataTable: 'Data Table',
    ordersCrud: 'Orders CRUD',
    save: 'Save',
    cancel: 'Cancel',
    theme: 'Theme',
    language: 'Language',
    darkMode: 'Dark Mode',
    lightMode: 'Light Mode',
    general: 'General',
    display: 'Display',
    notifications: 'Notifications',
  },
  zh: {
    login: '登录',
    logout: '退出',
    email: '邮箱',
    password: '密码',
    loginTitle: '登录管理后台',
    loginBtn: '登录',
    loginError: '邮箱或密码错误',
    settings: '设置',
    profile: '个人资料',
    dashboard: '仪表盘',
    dataTable: '数据表格',
    ordersCrud: '订单管理',
    save: '保存',
    cancel: '取消',
    theme: '主题',
    language: '语言',
    darkMode: '深色模式',
    lightMode: '浅色模式',
    general: '常规',
    display: '显示',
    notifications: '通知',
  },
};

type Locale = 'en' | 'zh';

interface I18nContextType {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(() => {
    const stored = localStorage.getItem('locale');
    return (stored === 'zh' ? 'zh' : 'en') as Locale;
  });

  const setLocaleAndPersist = useCallback((l: Locale) => {
    setLocale(l);
    localStorage.setItem('locale', l);
  }, []);

  const t = useCallback(
    (key: string) => messages[locale]?.[key] || messages.en[key] || key,
    [locale],
  );

  return (
    <I18nContext.Provider value={{ locale, setLocale: setLocaleAndPersist, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}
