import { useMemo, useState } from 'react';
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

const STATUS_COLORS: Record<string, string> = {
  completed: 'green',
  pending: 'gold',
  cancelled: 'red',
};
const STATUS_FALLBACK_COLOR = 'default';

const STATUS_OPTIONS: { value: string; text: string }[] = [
  { value: 'completed', text: 'Completed' },
  { value: 'pending', text: 'Pending' },
  { value: 'cancelled', text: 'Cancelled' },
];

const STATUS_SELECT_OPTIONS = STATUS_OPTIONS.map(({ value, text }) => ({
  value,
  label: text,
}));

export default function DataTablePage() {
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  const filteredData = useMemo(() => {
    return mockData.filter((item) => {
      const matchSearch = !searchText
        || item.customer.toLowerCase().includes(searchText.toLowerCase());
      const matchStatus = !statusFilter || item.status === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [searchText, statusFilter]);

  const columns: ColumnsType<Order> = useMemo(() => [
    {
      title: 'Order ID',
      dataIndex: 'id',
      sorter: (a, b) => a.id.localeCompare(b.id),
    },
    { title: 'Customer', dataIndex: 'customer' },
    {
      title: 'Amount',
      dataIndex: 'amount',
      sorter: (a, b) => a.amount - b.amount,
      render: (v: number) => `$${v.toLocaleString()}`,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      filters: STATUS_OPTIONS,
      filteredValue: statusFilter ? [statusFilter] : null,
      onFilter: (value, record) => record.status === value,
      render: (s: string) => (
        <Tag color={STATUS_COLORS[s] || STATUS_FALLBACK_COLOR}>
          {s.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Date',
      dataIndex: 'date',
      sorter: (a, b) => a.date.localeCompare(b.date),
      render: (d: string) => dayjs(d).format('MMM D, YYYY'),
    },
  ], []);

  return (
    <Card title="Orders">
      <Space style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="Search customer..."
          onChange={(e) => setSearchText(e.target.value)}
          onSearch={setSearchText}
          style={{ width: 240 }}
          allowClear
        />
        <Select
          placeholder="Filter status"
          allowClear
          style={{ width: 160 }}
          onChange={(v) => setStatusFilter(v || null)}
          options={STATUS_SELECT_OPTIONS}
        />
      </Space>
      <Table
        columns={columns}
        dataSource={filteredData}
        pagination={{ pageSize: 5, showSizeChanger: true }}
        locale={{ emptyText: 'No orders found' }}
      />
    </Card>
  );
}
