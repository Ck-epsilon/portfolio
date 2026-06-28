// Author: Ck.epsilon
/** Settings page with theme/language toggles and notification prefs. */

import { Card, Switch, Select, Divider, Typography, Space, Tag } from 'antd';
import { BulbOutlined, TranslationOutlined, BellOutlined } from '@ant-design/icons';
import { useI18n } from './I18nContext';

const { Title, Text } = Typography;

interface Props {
  isDark: boolean;
  toggleDark: () => void;
}

export default function SettingsPage({ isDark, toggleDark }: Props) {
  const { locale, setLocale, t } = useI18n();

  return (
    <div style={{ maxWidth: 600 }}>
      <Title level={4}>{t('settings')}</Title>

      <Card style={{ marginBottom: 16 }}>
        <Title level={5}><BulbOutlined /> {t('display')}</Title>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{t('darkMode')}</span>
            <Switch checked={isDark} onChange={toggleDark} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{t('language')}</span>
            <Select
              value={locale}
              onChange={(v) => setLocale(v)}
              style={{ width: 120 }}
              options={[
                { value: 'en', label: 'English' },
                { value: 'zh', label: '中文' },
              ]}
            />
          </div>
        </Space>
      </Card>

      <Card style={{ marginBottom: 16 }}>
        <Title level={5}><BellOutlined /> {t('notifications')}</Title>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Email notifications</span>
            <Switch defaultChecked />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Push notifications</span>
            <Switch />
          </div>
        </Space>
      </Card>

      <Card>
        <Title level={5}>{t('general')}</Title>
        <Text type="secondary">
          Version: 1.0.0 · Built with React + Ant Design + Vite
        </Text>
      </Card>
    </div>
  );
}
