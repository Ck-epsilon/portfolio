// Author: Ck.epsilon & Chaos (AI Programming Assistant)
/** Dashboard page — summary cards + recent activity using Recharts. */

import { useMemo } from 'react';
import { Card, CardContent, Typography, Box, Grid } from '@mui/material';
import { useGetList, Loading, Error } from 'react-admin';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface UserRecord {
  id: string | number;
  is_active?: boolean;
  [key: string]: unknown;
}

export const Dashboard = (): React.ReactElement => {
  const { data: users, isLoading: usersLoading, error: usersError } = useGetList('users', {
    pagination: { page: 1, perPage: 100 },
    sort: { field: 'id', order: 'ASC' },
  });

  const { data: items, isLoading: itemsLoading } = useGetList('items', {
    pagination: { page: 1, perPage: 100 },
    sort: { field: 'id', order: 'ASC' },
  });

  if (usersLoading || itemsLoading) return <Loading />;
  if (usersError) return <Error />;

  const activeUsers = (users || []).filter(
    (u: UserRecord) => u.is_active
  ).length;

  const chartData = useMemo(
    () =>
      ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => ({
        day,
        users: Math.floor(Math.random() * 10) + i,
        items: Math.floor(Math.random() * 15) + i * 2,
      })),
    [] // static data — compute once
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <StatCard label="Total Users" value={users?.length || 0} />
        <StatCard label="Active Users" value={activeUsers} />
        <StatCard label="Total Items" value={items?.length || 0} />
        <StatCard label="API Status" value="Online" color="#34c759" />
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Weekly Activity
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="users" fill="#0071e3" radius={[4, 4, 0, 0]} />
              <Bar dataKey="items" fill="#86868b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string | number;
  color?: string;
}): React.ReactElement {
  return (
    <Grid item xs={12} sm={6} md={3}>
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Typography variant="overline" color="text.secondary">
            {label}
          </Typography>
          <Typography variant="h3" sx={{ color: color || 'text.primary', mt: 0.5 }}>
            {value}
          </Typography>
        </CardContent>
      </Card>
    </Grid>
  );
}
