"use client";

import { useCallback, useEffect, useState } from "react";

export type AsyncResource<T> = {
  data: T;
  isLoading: boolean;
  error: string | null;
  reload: () => Promise<void>;
};

export function useAsyncResource<T>(
  loader: () => Promise<T>,
  initialValue: T,
): AsyncResource<T> {
  const [data, setData] = useState<T>(initialValue);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setData(await loader());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  }, [loader]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { data, isLoading, error, reload };
}
