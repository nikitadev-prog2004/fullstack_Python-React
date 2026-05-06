"use client";

import { useCallback } from "react";
import { useAsyncResource } from "../../shared/hooks/useAsyncResource";
import { alertsApi } from "./api";

export function useAlerts() {
  const loader = useCallback(() => alertsApi.list(), []);
  return useAsyncResource(loader, []);
}
