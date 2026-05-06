"use client";

import { useCallback } from "react";
import { useAsyncResource } from "../../shared/hooks/useAsyncResource";
import { filesApi } from "./api";

export function useFiles() {
  const loader = useCallback(() => filesApi.list(), []);
  return useAsyncResource(loader, []);
}
