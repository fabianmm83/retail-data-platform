// Formato de moneda en MXN
export const formatCurrency = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
};

// Formato de moneda con decimales
export const formatCurrencyPrecise = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
};

// Formato de número con separadores
export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('es-MX').format(value);
};

// Formato de porcentaje
export const formatPercent = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return `${(num * 100).toFixed(1)}%`;
};

// Formato de fecha corta (dd/mm)
export const formatDateShort = (iso: string): string => {
  const d = new Date(iso + 'T00:00:00');
  return `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1).toString().padStart(2, '0')}`;
};

// Formato de fecha larga
export const formatDateLong = (iso: string): string => {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};