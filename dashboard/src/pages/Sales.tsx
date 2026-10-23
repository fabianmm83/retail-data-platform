import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
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
import { useRevenueByChannel, useRevenueDaily, useOverview } from '../lib/hooks';
import {
  formatCurrency,
  formatDateShort,
  formatNumber,
  formatPercent,
} from '../lib/format';

const CHANNEL_COLORS: Record<string, string> = {
  ONLINE: '#6366f1',
  STORE: '#f59e0b',
};

export default function Sales() {
  const overview = useOverview();
  const daily = useRevenueDaily();
  const channels = useRevenueByChannel();

  if (daily.isLoading) return <Loading />;
  if (daily.isError) return <ErrorState />;

  // Preparar data para el AreaChart (agregar campo "revenue_num" para el eje Y)
  const chartData = (daily.data ?? []).map((p) => ({
    ...p,
    revenue_num: parseFloat(p.revenue),
  }));

  return (
    <>
      <PageHeader
        title="Sales"
        subtitle="Análisis de ventas y evolución temporal"
      />

      {/* KPIs de ventas */}
      <Grid cols={4} gap={4}>
        <KPICard
          title="Revenue Total"
          value={overview.data ? formatCurrency(overview.data.total_revenue) : '—'}
          accent="success"
        />
        <KPICard
          title="Órdenes"
          value={overview.data ? formatNumber(overview.data.total_orders) : '—'}
        />
        <KPICard
          title="Unidades Vendidas"
          value={overview.data ? formatNumber(overview.data.total_units) : '—'}
        />
        <KPICard
          title="AOV"
          value={overview.data ? formatCurrency(overview.data.aov) : '—'}
          accent="info"
        />
      </Grid>

      {/* Serie temporal */}
      <div className="mt-6 sm:mt-8 card">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
          <h3 className="text-base font-semibold text-gray-900">
            Revenue en el tiempo
          </h3>
          <p className="text-xs text-gray-500">
            {chartData.length} {chartData.length === 1 ? 'día' : 'días'}
          </p>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDateShort}
              tick={{ fontSize: 12 }}
            />
            <YAxis
              tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value) =>
                typeof value === 'number'
                  ? formatCurrency(value)
                  : String(value ?? '')
              }
              labelFormatter={(label) => `Fecha: ${label}`}
            />
            <Area
              type="monotone"
              dataKey="revenue_num"
              stroke="#6366f1"
              strokeWidth={2}
              fill="url(#revenueGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Comparación por canal */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar chart: revenue por canal */}
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Revenue por Canal
          </h3>
          {channels.isLoading ? (
            <Loading />
          ) : channels.isError ? (
            <ErrorState />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={channels.data}
                margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="channel" tick={{ fontSize: 12 }} />
                <YAxis
                  tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  formatter={(value) =>
                    typeof value === 'number'
                      ? formatCurrency(value)
                      : String(value ?? '')
                  }
                />
                <Bar dataKey="revenue" radius={[4, 4, 0, 0]}>
                  {channels.data?.map((entry) => (
                    <Cell
                      key={entry.channel}
                      fill={CHANNEL_COLORS[entry.channel] || '#999'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Tabla de detalle por canal */}
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Detalle por Canal
          </h3>
          {channels.isLoading ? (
            <Loading />
          ) : channels.isError ? (
            <ErrorState />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 font-medium text-gray-600">
                      Canal
                    </th>
                    <th className="text-right py-2 font-medium text-gray-600">
                      Revenue
                    </th>
                    <th className="text-right py-2 font-medium text-gray-600">
                      Órdenes
                    </th>
                    <th className="text-right py-2 font-medium text-gray-600">
                      AOV
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {channels.data?.map((c) => (
                    <tr key={c.channel} className="border-b border-gray-100">
                      <td className="py-3">
                        <span
                          className="inline-block w-3 h-3 rounded-full mr-2"
                          style={{
                            backgroundColor: CHANNEL_COLORS[c.channel] || '#999',
                          }}
                        />
                        {c.channel}
                      </td>
                      <td className="py-3 text-right font-medium">
                        {formatCurrency(c.revenue)}
                      </td>
                      <td className="py-3 text-right">
                        {formatNumber(c.orders)}
                      </td>
                      <td className="py-3 text-right">
                        {formatCurrency(c.aov)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Online share como footer */}
          {overview.data && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">Online share</p>
              <p className="text-2xl font-bold text-brand-600">
                {formatPercent(overview.data.online_share)}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Meta: &gt; 50% ✓
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Comparación de unidades vs revenue */}
      <div className="mt-6 card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">
          Unidades vs Revenue por día
        </h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDateShort}
              tick={{ fontSize: 12 }}
            />
            <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
            <YAxis
              yAxisId="right"
              orientation="right"
              tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value, name) =>
                typeof value === 'number'
                  ? name === 'revenue_num'
                    ? formatCurrency(value)
                    : formatNumber(value)
                  : String(value ?? '')
              }
            />
            <Legend />
            <Bar
              yAxisId="left"
              dataKey="units"
              fill="#10b981"
              name="Unidades"
              radius={[4, 4, 0, 0]}
            />
            <Bar
              yAxisId="right"
              dataKey="revenue_num"
              fill="#6366f1"
              name="Revenue"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}