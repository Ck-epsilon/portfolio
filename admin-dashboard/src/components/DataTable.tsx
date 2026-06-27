import { useState } from 'react';
import { Table, Tag, Input, Select, Space, Card } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

interface Order {
  key: string;
  id: string;
  customer: string;
  amount: number;
  status: 'completed' | 'pending' | 'cancelled';
  date: string;
}

const mockData: Order[] = [
  { key: '1', id: 'ORD-001', customer: 'Alice Johnson', amount: 1250, status: 'completed', date: '2026-06-25' },
  { key: '2', id: 'ORD-002', customer: 'Bob Smith', amount: 890, status: 'pending', date: '2026-06-25' },
  { key: '3', id: 'ORD-003', customer: 'Carol White', amount: 2340, status: 'completed', date: '2026-06-26' },
  { key: '4', id: 'ORD-004', customer: 'Dave Lee', amount: 560, status: 'cancelled', date: '2026-06-26' },
  { key: '5', id: 'ORD-005', customer: 'Eve Chen', amount: 1890, status: 'pending', date: '2026-06-27' },
  { key: '6', id: 'ORD-006', customer: 'Frank Wu', amount: 3100, status: 'completed', date: '2026-06-27' },
  { key: '7', id: 'ORD-007', customer: 'Grace Kim', amount: 720, status: 'pending', date: '2026-06-27' },
];

const statusColors: Record<string, string> = {
  completed: 'green',
  pending: 'gold',
  cancelled: 'red',
};

export default function DataTablePage() {
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  const columns: ColumnsType<Order> = [
    { title: 'Order ID', dataIndex: 'id', key: 'id', sorter: (a, b) => a.id.localeCompare(b.id) },
    { title: 'Customer', dataIndex: 'customer', key: 'customer',
      filteredValue: searchText ? [searchText] : null,
      onFilter: (_, record) => record.customer.toLowerCase().includes(searchText.toLowerCase()),
    },
    {
      title: 'Amount', dataIndex: 'amount', key: 'amount',
      sorter: (a, b) => a.amount - b.amount,
      render: (v: number) => `$${v.toLocaleString()}`,
    },
    {
      title: 'Status', dataIndex: 'status', key: 'status',
      filteredValue: statusFilter ? [statusFilter] : null,
      onFilter: (_, record) => !statusFilter || record.status === statusFilter,
      render: (s: string) => <Tag color={statusColors[s]}>{s.toUpperCase()}</Tag>,
    },
    {
      title: 'Date', dataIndex: 'date', key: 'date',
      sorter: (a, b) => a.date.localeCompare(b.date),
      render: (d: string) => dayjs(d).format('MMM D, YYYY'),
    },
  ];

  return (
    <Card title="Orders">
      <Space style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="Search customer..."
          onSearch={setSearchText}
          style={{ width: 240 }}
          allowClear
        />
        <Select
          placeholder="Filter status"
          allowClear
          style={{ width: 160 }}
          onChange={(v) => setStatusFilter(v || null)}
          options={[
            { value: 'completed', label: 'Completed' },
            { value: 'pending', label: 'Pending' },
            { value: 'cancelled', label: 'Cancelled' },
          ]}
        />
      </Space>
      <Table
        columns={columns}
        dataSource={mockData}
        pagination={{ pageSize: 5, showSizeChanger: true }}
      />
    </Card>
  );
}
