import { useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
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
import { useRevenueByProduct } from '../lib/hooks';
import { formatCurrency, formatNumber } from '../lib/format';

type SortKey = 'revenue' | 'units' | 'orders' | 'avg_price';

const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: 'revenue', label: 'Revenue' },
  { key: 'units', label: 'Unidades' },
  { key: 'orders', label: 'Órdenes' },
  { key: 'avg_price', label: 'Precio Promedio' },
];

export default function Products() {
  const { data, isLoading, isError } = useRevenueByProduct(32);
  const [sortKey, setSortKey] = useState<SortKey>('revenue');

  if (isLoading) return <Loading />;
  if (isError) return <ErrorState />;
  if (!data) return null;

  // Ordenar según el sortKey
  const sorted = [...data].sort((a, b) => {
    const aVal = parseFloat(a[sortKey] as string);
    const bVal = parseFloat(b[sortKey] as string);
    return bVal - aVal;
  });

  const top10 = sorted.slice(0, 10);

  // Agregados
  const totalRevenue = data.reduce(
    (sum, p) => sum + parseFloat(p.revenue),
    0,
  );
  const totalUnits = data.reduce((sum, p) => sum + p.units, 0);
  const totalOrders = data.reduce((sum, p) => sum + p.orders, 0);

  // Chart data
  const chartData = top10.map((p) => ({
    ...p,
    revenue_num: parseFloat(p.revenue),
    short_name:
      p.product_name.length > 30
        ? p.product_name.substring(0, 30) + '…'
        : p.product_name,
  }));

  return (
    <>
      <PageHeader
        title="Products"
        subtitle="Top productos por revenue y performance"
      />

      {/* KPIs agregados */}
      <Grid cols={4} gap={4}>
        <KPICard
          title="Productos Vendidos"
          value={formatNumber(data.length)}
          accent="info"
        />
        <KPICard
          title="Revenue Total"
          value={formatCurrency(totalRevenue)}
          accent="success"
        />
        <KPICard
          title="Unidades Totales"
          value={formatNumber(totalUnits)}
        />
        <KPICard
          title="Órdenes Totales"
          value={formatNumber(totalOrders)}
        />
      </Grid>

      {/* Top 10 chart */}
      <div className="mt-6 sm:mt-8 card">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
          <h3 className="text-base font-semibold text-gray-900">
            Top 10 Productos por Revenue
          </h3>
        </div>
        <ResponsiveContainer width="100%" height={380}>
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
              dataKey="short_name"
              width={200}
              tick={{ fontSize: 10 }}
            />
            <Tooltip
              formatter={(value) =>
                typeof value === 'number'
                  ? formatCurrency(value)
                  : String(value ?? '')
              }
            />
            <Bar dataKey="revenue_num" fill="#6366f1" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Tabla completa */}
      <div className="mt-6 card">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <h3 className="text-base font-semibold text-gray-900">
            Todos los Productos
          </h3>
          <div className="flex flex-wrap gap-2">
            {SORT_OPTIONS.map((opt) => (
              <button
                key={opt.key}
                onClick={() => setSortKey(opt.key)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                  sortKey === opt.key
                    ? 'bg-brand-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-2 font-medium text-gray-600">
                  #
                </th>
                <th className="text-left py-2 px-2 font-medium text-gray-600">
                  Style
                </th>
                <th className="text-left py-2 px-2 font-medium text-gray-600">
                  Producto
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
                  Precio Prom.
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((p, idx) => (
                <tr key={p.product_key} className="border-b border-gray-100">
                  <td className="py-3 px-2 text-gray-400 text-xs">
                    {idx + 1}
                  </td>
                  <td className="py-3 px-2 font-mono text-xs text-gray-600">
                    {p.style_code}
                  </td>
                  <td className="py-3 px-2 font-medium text-gray-900">
                    {p.product_name}
                  </td>
                  <td className="py-3 px-2 text-right font-semibold">
                    {formatCurrency(p.revenue)}
                  </td>
                  <td className="py-3 px-2 text-right">
                    {formatNumber(p.units)}
                  </td>
                  <td className="py-3 px-2 text-right text-gray-600">
                    {formatNumber(p.orders)}
                  </td>
                  <td className="py-3 px-2 text-right text-gray-600">
                    {formatCurrency(p.avg_price)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}