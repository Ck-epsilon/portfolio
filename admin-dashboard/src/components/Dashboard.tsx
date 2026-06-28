// Author: Ck.epsilon
import { Card, Col, Row, Statistic } from 'antd';
import {
  UserOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

const revenueData = [
  { month: 'Jan', revenue: 4000, orders: 240 },
  { month: 'Feb', revenue: 3000, orders: 198 },
  { month: 'Mar', revenue: 5000, orders: 305 },
  { month: 'Apr', revenue: 4780, orders: 290 },
  { month: 'May', revenue: 5890, orders: 340 },
  { month: 'Jun', revenue: 6390, orders: 385 },
];

const trafficData = [
  { source: 'Direct', visits: 4500 },
  { source: 'Social', visits: 3200 },
  { source: 'Referral', visits: 2100 },
  { source: 'Email', visits: 1800 },
  { source: 'Ads', visits: 1400 },
];

export default function DashboardPage() {
  return (
    <>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="Total Users" value={12846} prefix={<UserOutlined />} /></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="Orders" value={885} prefix={<ShoppingCartOutlined />} /></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="Revenue" value={89320} prefix={<DollarOutlined />} precision={0} /></Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card><Statistic title="Growth" value="+18.2%" prefix={<RiseOutlined />} valueStyle={{ color: '#52c41a' }} /></Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={16}>
          <Card title="Revenue Trend">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="revenue" stroke="#1677ff" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Traffic Sources">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trafficData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="source" type="category" width={70} />
                <Tooltip />
                <Bar dataKey="visits" fill="#1677ff" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </>
  );
}
