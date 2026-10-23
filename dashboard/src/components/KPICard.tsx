interface KPICardProps {
  title: string;
  value: string;
  subtitle?: string;
  accent?: 'default' | 'success' | 'warning' | 'info';
}

const ACCENT_CLASSES = {
  default: 'text-gray-900',
  success: 'text-green-600',
  warning: 'text-orange-600',
  info: 'text-brand-600',
};

export default function KPICard({
  title,
  value,
  subtitle,
  accent = 'default',
}: KPICardProps) {
  return (
    <div className="card">
      <p className="card-title">{title}</p>
      <p className={`card-value ${ACCENT_CLASSES[accent]}`}>{value}</p>
      {subtitle && <p className="text-xs text-gray-500 mt-2">{subtitle}</p>}
    </div>
  );
}