// Author: Ck.epsilon
/** Login page with form validation. */

import { useState } from 'react';
import { Card, Form, Input, Button, Typography, Alert, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from './AuthContext';
import { useI18n } from './I18nContext';

const { Title } = Typography;

export default function LoginPage() {
  const { login } = useAuth();
  const { t } = useI18n();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (values: { email: string; password: string }) => {
    setLoading(true);
    setError('');
    try {
      await login(values.email, values.password);
    } catch {
      setError(t('loginError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex', justifyContent: 'center', alignItems: 'center',
      minHeight: '100vh', background: '#f0f2f5', padding: 16,
    }}>
      <Card style={{ width: 400, maxWidth: '100%' }}>
        <Title level={3} style={{ textAlign: 'center', marginBottom: 24 }}>
          {t('loginTitle')}
        </Title>
        {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} showIcon />}
        <Form onFinish={handleSubmit} layout="vertical" size="large">
          <Form.Item name="email" rules={[{ required: true, type: 'email', message: t('email') }]}>
            <Input prefix={<UserOutlined />} placeholder={t('email')} />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: t('password') }]}>
            <Input.Password prefix={<LockOutlined />} placeholder={t('password')} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              {t('loginBtn')}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
