import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import ErrorState from '../components/ErrorState';
import Grid from '../components/Grid';
import KPICard from '../components/KPICard';
import Loading from '../components/Loading';
import PageHeader from '../components/PageHeader';
import { useOverview, useRevenueByCategory, useRevenueByChannel } from '../lib/hooks';
import { formatCurrency, formatNumber, formatPercent } from '../lib/format';

const CHANNEL_COLORS: Record<string, string> = {
  ONLINE: '#6366f1',
  STORE: '#f59e0b',
};

export default function Overview() {
  const overview = useOverview();
  const channels = useRevenueByChannel();
  const categories = useRevenueByCategory();

  if (overview.isLoading) return <Loading />;
  if (overview.isError) return <ErrorState />;
  if (!overview.data) return null;

  const data = overview.data;

  return (
    <>
      <PageHeader
        title="Overview"
        subtitle="Snapshot general del negocio"
      />

      {/* KPIs principales */}
      <Grid cols={4} gap={4}>
        <KPICard
          title="Revenue Total"
          value={formatCurrency(data.total_revenue)}
          accent="success"
        />
        <KPICard
          title="Órdenes"
          value={formatNumber(data.total_orders)}
        />
        <KPICard
          title="Unidades Vendidas"
          value={formatNumber(data.total_units)}
        />
        <KPICard
          title="Ticket Promedio (AOV)"
          value={formatCurrency(data.aov)}
          accent="info"
        />
      </Grid>

      {/* Segunda fila */}
      <div className="mt-4 sm:mt-6">
        <Grid cols={4} gap={4}>
          <KPICard
            title="Online Share"
            value={formatPercent(data.online_share)}
            subtitle="Meta: > 50%"
            accent={parseFloat(data.online_share) > 0.5 ? 'success' : 'warning'}
          />
          <KPICard title="Top Estado" value={data.top_state} />
          <KPICard title="Top Categoría" value={data.top_category} />
          <KPICard
            title="Revenue Online"
            value={formatCurrency(data.online_revenue)}
          />
        </Grid>
      </div>

      {/* Gráficos */}
      <div className="mt-6 sm:mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie por canal */}
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Distribución por Canal
          </h3>
          {channels.isLoading ? (
            <Loading />
          ) : channels.isError ? (
            <ErrorState />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={channels.data}
                  dataKey="revenue"
                  nameKey="channel"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                   label={(props) => props.name ?? ''}
                >
                  {channels.data?.map((entry) => (
                    <Cell
                      key={entry.channel}
                      fill={CHANNEL_COLORS[entry.channel] || '#999'}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) =>
                    typeof value === 'number'
                      ? formatCurrency(value)
                      : String(value ?? '')
                  }
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Bar por categoría */}
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Revenue por Categoría
          </h3>
          {categories.isLoading ? (
            <Loading />
          ) : categories.isError ? (
            <ErrorState />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={categories.data}
                layout="vertical"
                margin={{ left: 20, right: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  type="number"
                  tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`}
                />
                <YAxis
                  type="category"
                  dataKey="category_code"
                  width={100}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip
                  formatter={(value) =>
                    typeof value === 'number'
                      ? formatCurrency(value)
                      : String(value ?? '')
                  }
                />
                <Bar dataKey="revenue" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </>
  );
}