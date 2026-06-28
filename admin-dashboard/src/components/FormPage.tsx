// Author: Ck.epsilon
/** Order CRUD form page with validation and API integration. */

import { useState, useEffect, useMemo } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, InputNumber, Select, Popconfirm,
  Space, message, Tag, Typography,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import client from '../api/client';
import type { Order, OrderFormValues } from '../types/order';

const { Title } = Typography;

const STATUS_COLORS: Record<string, string> = {
  completed: 'green',
  pending: 'gold',
  cancelled: 'red',
};

const STATUS_OPTIONS = [
  { label: 'Completed', value: 'completed' },
  { label: 'Pending', value: 'pending' },
  { label: 'Cancelled', value: 'cancelled' },
];

export default function FormPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Order | null>(null);
  const [form] = Form.useForm<OrderFormValues>();

  // Fetch from API
  const fetchOrders = async () => {
    setLoading(true);
    try {
      const { data } = await client.get<Order[]>('/users/me/items');
      setOrders(data);
    } catch {
      message.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrders(); }, []);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const openEdit = (order: Order) => {
    setEditing(order);
    form.setFieldsValue({
      customer: order.customer,
      amount: order.amount,
      status: order.status,
    });
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await client.delete(`/orders/${id}`);
      message.success('Deleted');
      fetchOrders();
    } catch {
      message.error('Delete failed');
    }
  };

  const handleSubmit = async () => {
    const values = await form.validateFields();
    try {
      if (editing) {
        await client.patch(`/orders/${editing.id}`, values);
        message.success('Updated');
      } else {
        await client.post('/orders', values);
        message.success('Created');
      }
      setModalOpen(false);
      fetchOrders();
    } catch {
      message.error('Save failed');
    }
  };

  const columns: ColumnsType<Order> = useMemo(() => [
    { title: 'ID', dataIndex: 'id', sorter: (a, b) => a.id.localeCompare(b.id) },
    { title: 'Customer', dataIndex: 'customer', sorter: (a, b) => a.customer.localeCompare(b.customer) },
    {
      title: 'Amount',
      dataIndex: 'amount',
      sorter: (a, b) => a.amount - b.amount,
      render: (v: number) => `$${v.toLocaleString()}`,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      render: (s: string) => <Tag color={STATUS_COLORS[s] || 'default'}>{s.toUpperCase()}</Tag>,
    },
    { title: 'Date', dataIndex: 'date', sorter: (a, b) => a.date.localeCompare(b.date) },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
          <Popconfirm title="Delete this order?" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ], []);

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={4}>Orders — CRUD</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          New Order
        </Button>
      </div>

      <Card>
        <Table<Order>
          columns={columns}
          dataSource={orders}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editing ? 'Edit Order' : 'New Order'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item name="customer" label="Customer" rules={[{ required: true, min: 2 }]}>
            <Input />
          </Form.Item>
          <Form.Item name="amount" label="Amount" rules={[{ required: true, type: 'number', min: 1 }]}>
            <InputNumber style={{ width: '100%' }} min={1} prefix="$" />
          </Form.Item>
          <Form.Item name="status" label="Status" rules={[{ required: true }]}>
            <Select options={STATUS_OPTIONS} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
