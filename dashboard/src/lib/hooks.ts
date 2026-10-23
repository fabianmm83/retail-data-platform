import { useQuery } from '@tanstack/react-query';

import {
  getLogistics,
  getOverview,
  getRevenueByCategory,
  getRevenueByChannel,
  getRevenueByProduct,
  getRevenueByState,
  getRevenueDaily,
} from './api';

export const useOverview = () =>
  useQuery({
    queryKey: ['overview'],
    queryFn: getOverview,
  });

export const useRevenueDaily = () =>
  useQuery({
    queryKey: ['revenue-daily'],
    queryFn: getRevenueDaily,
  });

export const useRevenueByProduct = (limit = 32) =>
  useQuery({
    queryKey: ['revenue-by-product', limit],
    queryFn: () => getRevenueByProduct(limit),
  });

export const useRevenueByState = () =>
  useQuery({
    queryKey: ['revenue-by-state'],
    queryFn: getRevenueByState,
  });

export const useRevenueByChannel = () =>
  useQuery({
    queryKey: ['revenue-by-channel'],
    queryFn: getRevenueByChannel,
  });

export const useRevenueByCategory = () =>
  useQuery({
    queryKey: ['revenue-by-category'],
    queryFn: getRevenueByCategory,
  });

export const useLogistics = () =>
  useQuery({
    queryKey: ['logistics'],
    queryFn: getLogistics,
  });