import axios from 'axios';

export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
});

// =============================================================================
// TIPOS
// =============================================================================

export interface OverviewKPI {
  total_revenue: string;
  total_orders: number;
  total_units: number;
  aov: string;
  online_revenue: string;
  store_revenue: string;
  online_share: string;
  top_state: string;
  top_category: string;
}

export interface RevenueDailySeriesPoint {
  date: string;
  revenue: string;
  orders: number;
  units: number;
}

export interface RevenueByProduct {
  product_key: number;
  style_code: string;
  product_name: string;
  year: number;
  month: number;
  revenue: string;
  units: number;
  orders: number;
  avg_price: string;
}

export interface RevenueByState {
  state_code: string;
  state_name: string;
  revenue: string;
  units: number;
  orders: number;
  aov: string;
}

export interface RevenueByChannel {
  channel: string;
  revenue: string;
  units: number;
  orders: number;
  aov: string;
}

export interface RevenueByCategory {
  category_code: string;
  revenue: string;
  units: number;
  orders: number;
  aov: string;
}

// =============================================================================
// ENDPOINTS
// =============================================================================

export const getOverview = async (): Promise<OverviewKPI> => {
  const { data } = await api.get('/kpis/overview');
  return data;
};

export const getRevenueDaily = async (): Promise<RevenueDailySeriesPoint[]> => {
  const { data } = await api.get('/kpis/revenue/daily');
  return data;
};

export const getRevenueByProduct = async (limit = 32): Promise<RevenueByProduct[]> => {
  const { data } = await api.get('/kpis/revenue/products', { params: { limit } });
  return data;
};

export const getRevenueByState = async (): Promise<RevenueByState[]> => {
  const { data } = await api.get('/kpis/revenue/states');
  return data;
};

export const getRevenueByChannel = async (): Promise<RevenueByChannel[]> => {
  const { data } = await api.get('/kpis/revenue/channels');
  return data;
};

export const getRevenueByCategory = async (): Promise<RevenueByCategory[]> => {
  const { data } = await api.get('/kpis/revenue/categories');
  return data;
};


export interface LogisticsPerformance {
  year: number;
  month: number;
  shipments: number;
  delivered: number;
  delayed: number;
  in_transit: number;
  on_time_rate: string;
  avg_lead_time_days: string;
  avg_shipping_cost: string;
  total_shipping_cost: string;
}

export const getLogistics = async (): Promise<LogisticsPerformance[]> => {
  const { data } = await api.get('/kpis/logistics');
  return data;
};