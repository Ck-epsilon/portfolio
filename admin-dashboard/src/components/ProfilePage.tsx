// Author: Ck.epsilon & Chaos (AI Programming Assistant)
/** User profile page with editable fields. */

import { Card, Descriptions, Button, Form, Input, message, Space, Tag } from 'antd';
import { UserOutlined, MailOutlined, CalendarOutlined } from '@ant-design/icons';
import { useAuth } from './AuthContext';
import { useI18n } from './I18nContext';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const { t } = useI18n();

  if (!user) return null;

  return (
    <>
      <Card title={t('profile')} style={{ maxWidth: 600 }}>
        <Descriptions column={1} bordered>
          <Descriptions.Item label={<><UserOutlined /> {t('profile')} Name</>}>
            {user.username}
          </Descriptions.Item>
          <Descriptions.Item label={<><MailOutlined /> {t('email')}</>}>
            {user.email}
          </Descriptions.Item>
          <Descriptions.Item label="ID">{user.id}</Descriptions.Item>
          <Descriptions.Item label={<><CalendarOutlined /> Account Status</>}>
            <Tag color="green">Active</Tag>
          </Descriptions.Item>
        </Descriptions>

        <Form layout="vertical" style={{ marginTop: 24 }}>
          <Form.Item label={t('profile')} Name">
            <Input defaultValue={user.username} />
          </Form.Item>
          <Form.Item label={t('email')}>
            <Input defaultValue={user.email} disabled />
          </Form.Item>
          <Space>
            <Button type="primary" onClick={() => message.info(t('save') + ' (demo)')}>
              {t('save')}
            </Button>
            <Button danger onClick={logout}>{t('logout')}</Button>
          </Space>
        </Form>
      </Card>
    </>
  );
}
