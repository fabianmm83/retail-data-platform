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
import { useLogistics } from '../lib/hooks';
import { formatCurrency, formatNumber, formatPercent } from '../lib/format';

const MONTH_NAMES = [
  'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
  'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic',
];

export default function Logistics() {
  const { data, isLoading, isError } = useLogistics();

  if (isLoading) return <Loading />;
  if (isError) return <ErrorState />;
  if (!data || data.length === 0) return null;

  // Agregados totales
  const totalShipments = data.reduce((sum, r) => sum + r.shipments, 0);
  const totalDelivered = data.reduce((sum, r) => sum + r.delivered, 0);
  const totalDelayed = data.reduce((sum, r) => sum + r.delayed, 0);
  const totalInTransit = data.reduce((sum, r) => sum + r.in_transit, 0);
  const totalShippingCost = data.reduce(
    (sum, r) => sum + parseFloat(r.total_shipping_cost),
    0,
  );
  const avgShippingCost =
    totalShipments > 0 ? totalShippingCost / totalShipments : 0;

  const overallOnTimeRate =
    totalDelivered > 0
      ? data.reduce(
          (sum, r) =>
            sum + (parseFloat(r.on_time_rate) * r.delivered),
          0,
        ) / totalDelivered
      : 0;

  // Chart data
  const chartData = data.map((r) => ({
    label: `${MONTH_NAMES[r.month - 1]} ${r.year}`,
    shipments: r.shipments,
    delivered: r.delivered,
    delayed: r.delayed,
    in_transit: r.in_transit,
    shipping_cost: parseFloat(r.total_shipping_cost),
  }));

  return (
    <>
      <PageHeader
        title="Logistics"
        subtitle="Performance de envíos y carriers"
      />

      {/* KPIs */}
      <Grid cols={4} gap={4}>
        <KPICard
          title="Shipments Totales"
          value={formatNumber(totalShipments)}
          accent="info"
        />
        <KPICard
          title="Entregados"
          value={formatNumber(totalDelivered)}
          subtitle={`${formatPercent(
            totalShipments > 0 ? totalDelivered / totalShipments : 0,
          )} del total`}
          accent="success"
        />
        <KPICard
          title="En Tránsito"
          value={formatNumber(totalInTransit)}
          subtitle={`${formatNumber(totalDelayed)} retrasados`}
          accent="warning"
        />
        <KPICard
          title="Costo Total Envío"
          value={formatCurrency(totalShippingCost)}
          subtitle={`Promedio: ${formatCurrency(avgShippingCost)}`}
        />
      </Grid>

      {/* On-time rate */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            On-Time Delivery Rate
          </h3>
          <div className="flex items-end gap-4">
            <p className="text-4xl font-bold text-brand-600">
              {formatPercent(overallOnTimeRate)}
            </p>
            <p className="text-sm text-gray-500 mb-2">
              {formatNumber(totalDelivered)} de {formatNumber(totalShipments)}{' '}
              entregados a tiempo
            </p>
          </div>
          <div className="mt-4 h-3 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full"
              style={{ width: `${overallOnTimeRate * 100}%` }}
            />
          </div>
          {totalDelivered === 0 && (
            <p className="text-xs text-gray-500 mt-3">
              Sin shipments entregados todavía. Cuando el simulador corra más
              días, verás entregas aquí.
            </p>
          )}
        </div>

        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Distribución por Status
          </h3>
          <div className="space-y-3">
            {[
              {
                label: 'Entregados',
                value: totalDelivered,
                color: 'bg-green-500',
              },
              {
                label: 'En tránsito',
                value: totalInTransit,
                color: 'bg-brand-500',
              },
              {
                label: 'Retrasados',
                value: totalDelayed,
                color: 'bg-orange-500',
              },
            ].map((s) => (
              <div key={s.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-700">{s.label}</span>
                  <span className="font-medium">
                    {formatNumber(s.value)} (
                    {formatPercent(
                      totalShipments > 0 ? s.value / totalShipments : 0,
                    )}
                    )
                  </span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${s.color} rounded-full`}
                    style={{
                      width: `${
                        totalShipments > 0
                          ? (s.value / totalShipments) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Chart mensual */}
      <div className="mt-6 card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">
          Shipments por Mes
        </h3>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value, name) =>
                typeof value === 'number'
                  ? name === 'shipping_cost'
                    ? formatCurrency(value)
                    : formatNumber(value)
                  : String(value ?? '')
              }
            />
            <Bar
              dataKey="delivered"
              stackId="a"
              fill="#10b981"
              name="Entregados"
            />
            <Bar
              dataKey="in_transit"
              stackId="a"
              fill="#6366f1"
              name="En tránsito"
            />
            <Bar
              dataKey="delayed"
              stackId="a"
              fill="#f59e0b"
              name="Retrasados"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Tabla mensual */}
      <div className="mt-6 card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">
          Detalle Mensual
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-2 font-medium text-gray-600">
                  Mes
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  Shipments
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  Entregados
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  En tránsito
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  Retrasados
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  On-Time
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  Lead Time
                </th>
                <th className="text-right py-2 px-2 font-medium text-gray-600">
                  Costo Envío
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((r) => (
                <tr
                  key={`${r.year}-${r.month}`}
                  className="border-b border-gray-100"
                >
                  <td className="py-3 px-2 font-medium">
                    {MONTH_NAMES[r.month - 1]} {r.year}
                  </td>
                  <td className="py-3 px-2 text-right">
                    {formatNumber(r.shipments)}
                  </td>
                  <td className="py-3 px-2 text-right text-green-600 font-medium">
                    {formatNumber(r.delivered)}
                  </td>
                  <td className="py-3 px-2 text-right text-brand-600">
                    {formatNumber(r.in_transit)}
                  </td>
                  <td className="py-3 px-2 text-right text-orange-600">
                    {formatNumber(r.delayed)}
                  </td>
                  <td className="py-3 px-2 text-right">
                    {formatPercent(parseFloat(r.on_time_rate))}
                  </td>
                  <td className="py-3 px-2 text-right text-gray-600">
                    {r.delivered > 0
                      ? `${parseFloat(r.avg_lead_time_days).toFixed(1)} d`
                      : '—'}
                  </td>
                  <td className="py-3 px-2 text-right font-medium">
                    {formatCurrency(r.total_shipping_cost)}
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