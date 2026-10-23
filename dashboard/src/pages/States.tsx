import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
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
import { useRevenueByState } from '../lib/hooks';
import { formatCurrency, formatNumber, formatPercent } from '../lib/format';

export default function States() {
  const { data, isLoading, isError } = useRevenueByState();

  if (isLoading) return <Loading />;
  if (isError) return <ErrorState />;
  if (!data) return null;

  const totalRevenue = data.reduce(
    (sum, s) => sum + parseFloat(s.revenue),
    0,
  );

  const top3 = data.slice(0, 3);

  // Datos para el chart
  const chartData = data.map((s) => ({
    ...s,
    revenue_num: parseFloat(s.revenue),
  }));

  return (
    <>
      <PageHeader
        title="States"
        subtitle="Distribución geográfica del revenue"
      />

      {/* KPIs */}
      <Grid cols={4} gap={4}>
        <KPICard
          title="Estados Activos"
          value={formatNumber(data.length)}
          accent="info"
        />
        <KPICard
          title="Revenue Total"
          value={formatCurrency(totalRevenue)}
          accent="success"
        />
        <KPICard
          title="Top Estado"
          value={top3[0]?.state_name ?? '—'}
        />
        <KPICard
          title="Top Estado Share"
          value={
            top3[0] && totalRevenue > 0
              ? formatPercent(parseFloat(top3[0].revenue) / totalRevenue)
              : '—'
          }
        />
      </Grid>

      {/* Chart principal */}
      <div className="mt-6 sm:mt-8 card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">
          Revenue por Estado
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ left: 20, right: 20, top: 5, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`}
              tick={{ fontSize: 11 }}
            />
            <YAxis
              type="category"
              dataKey="state_code"
              width={70}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value) =>
                typeof value === 'number'
                  ? formatCurrency(value)
                  : String(value ?? '')
              }
            />
            <Bar dataKey="revenue_num" radius={[0, 4, 4, 0]}>
              {chartData.map((entry) => (
                <Cell
                  key={entry.state_code}
                  fill={
                    entry.state_code === 'CDMX' ||
                    entry.state_code === 'NL' ||
                    entry.state_code === 'JAL'
                      ? '#6366f1'
                      : entry.state_code === 'EDOMEX' ||
                        entry.state_code === 'QRO' ||
                        entry.state_code === 'PUE' ||
                        entry.state_code === 'BC'
                      ? '#818cf8'
                      : '#c7d2fe'
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-3 flex flex-wrap gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-[#6366f1]" /> ALTO
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-[#818cf8]" /> MEDIO
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-[#c7d2fe]" /> BAJO
          </div>
        </div>
      </div>

      {/* Tabla de detalle */}
      <div className="mt-6 card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">
          Detalle por Estado
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-2 font-medium text-gray-600">
                  #
                </th>
                <th className="text-left py-2 px-2 font-medium text-gray-600">
                  Estado
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  Revenue
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  Unidades
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  Órdenes
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  AOV
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  Share
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((s, idx) => {
                const share =
                  totalRevenue > 0
                    ? parseFloat(s.revenue) / totalRevenue
                    : 0;
                return (
                  <tr key={s.state_code} className="border-b border-gray-100">
                    <td className="py-3 px-2 text-gray-400 text-xs">
                      {idx + 1}
                    </td>
                    <td className="py-3 px-2">
                      <span className="font-mono text-xs text-gray-500 mr-2">
                        {s.state_code}
                      </span>
                      <span className="font-medium text-gray-900">
                        {s.state_name}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-right font-semibold">
                      {formatCurrency(s.revenue)}
                    </td>
                    <td className="py-3 px-2 text-right">
                      {formatNumber(s.units)}
                    </td>
                    <td className="py-3 px-2 text-right text-gray-600">
                      {formatNumber(s.orders)}
                    </td>
                    <td className="py-3 px-2 text-right text-gray-600">
                      {formatCurrency(s.aov)}
                    </td>
                    <td className="py-3 px-2 text-right text-gray-600">
                      {formatPercent(share)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}