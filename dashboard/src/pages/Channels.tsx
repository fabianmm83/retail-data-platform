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
import { useOverview, useRevenueByChannel } from '../lib/hooks';
import { formatCurrency, formatNumber, formatPercent } from '../lib/format';

const CHANNEL_COLORS: Record<string, string> = {
  ONLINE: '#6366f1',
  STORE: '#f59e0b',
};

export default function Channels() {
  const { data, isLoading, isError } = useRevenueByChannel();
  const overview = useOverview();

  if (isLoading) return <Loading />;
  if (isError) return <ErrorState />;
  if (!data) return null;

  const totalRevenue = data.reduce(
    (sum, c) => sum + parseFloat(c.revenue),
    0,
  );
  const totalOrders = data.reduce((sum, c) => sum + c.orders, 0);
  const totalUnits = data.reduce((sum, c) => sum + c.units, 0);

  const onlineData = data.find((c) => c.channel === 'ONLINE');
  const storeData = data.find((c) => c.channel === 'STORE');

  return (
    <>
      <PageHeader
        title="Channels"
        subtitle="Distribución online vs tienda física"
      />

      {/* KPIs */}
      <Grid cols={4} gap={4}>
        <KPICard
          title="Revenue Total"
          value={formatCurrency(totalRevenue)}
          accent="success"
        />
        <KPICard
          title="Online Share"
          value={
            overview.data
              ? formatPercent(overview.data.online_share)
              : formatPercent(
                  onlineData ? parseFloat(onlineData.revenue) / totalRevenue : 0,
                )
          }
          subtitle="Meta: > 50%"
          accent="info"
        />
        <KPICard
          title="Órdenes Totales"
          value={formatNumber(totalOrders)}
        />
        <KPICard
          title="Unidades Totales"
          value={formatNumber(totalUnits)}
        />
      </Grid>

      {/* Comparación visual */}
      <div className="mt-6 sm:mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie */}
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Distribución de Revenue
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                dataKey="revenue"
                nameKey="channel"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={(props) => {
                  const pct = totalRevenue > 0 && typeof props.percent === 'number'
                    ? formatPercent(props.percent)
                    : '';
                  return `${props.name ?? ''} ${pct}`;
                }}
              >
                {data.map((entry) => (
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
        </div>

        {/* Bar comparativo */}
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Revenue por Canal
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
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
                {data.map((entry) => (
                  <Cell
                    key={entry.channel}
                    fill={CHANNEL_COLORS[entry.channel] || '#999'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tarjetas detalladas por canal */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        {[onlineData, storeData].map((channel) => {
          if (!channel) return null;
          const share =
            totalRevenue > 0 ? parseFloat(channel.revenue) / totalRevenue : 0;

          return (
            <div key={channel.channel} className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-semibold text-gray-900">
                  {channel.channel}
                </h3>
                <span
                  className="inline-block w-4 h-4 rounded"
                  style={{
                    backgroundColor:
                      CHANNEL_COLORS[channel.channel] || '#999',
                  }}
                />
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-baseline">
                  <span className="text-sm text-gray-500">Revenue</span>
                  <span className="text-xl font-bold text-gray-900">
                    {formatCurrency(channel.revenue)}
                  </span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-sm text-gray-500">Órdenes</span>
                  <span className="text-base font-medium">
                    {formatNumber(channel.orders)}
                  </span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-sm text-gray-500">Unidades</span>
                  <span className="text-base font-medium">
                    {formatNumber(channel.units)}
                  </span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-sm text-gray-500">AOV</span>
                  <span className="text-base font-medium">
                    {formatCurrency(channel.aov)}
                  </span>
                </div>
                <div className="pt-3 border-t border-gray-200 flex justify-between items-baseline">
                  <span className="text-sm text-gray-500">Share</span>
                  <span className="text-lg font-bold text-brand-600">
                    {formatPercent(share)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Comparativa online vs store */}
      {onlineData && storeData && (
        <div className="mt-6 card bg-brand-50 border-brand-100">
          <h3 className="text-base font-semibold text-gray-900 mb-2">
            Insight: Online supera a Store
          </h3>
          <p className="text-sm text-gray-700">
            El canal ONLINE genera{' '}
            <strong>{formatCurrency(onlineData.revenue)}</strong> vs{' '}
            <strong>{formatCurrency(storeData.revenue)}</strong> del canal
            STORE, lo que representa un{' '}
            <strong>
              {formatPercent(
                (parseFloat(onlineData.revenue) /
                  parseFloat(storeData.revenue) -
                  1) *
                  1,
              )}
            </strong>{' '}
            más revenue en línea. La premisa del negocio (ONLINE &gt; STORE) se
            cumple.
          </p>
        </div>
      )}
    </>
  );
}