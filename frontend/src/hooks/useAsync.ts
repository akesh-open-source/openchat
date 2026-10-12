import { useCallback, useEffect, useRef, useState } from "react";

export interface AsyncState<T> {
  data: T | null;
  error: Error | null;
  loading: boolean;
}

export function useAsync<T>(
  factory: () => Promise<T>,
  deps: unknown[],
  options: { enabled?: boolean } = {},
): AsyncState<T> & { refetch: () => Promise<void> } {
  const enabled = options.enabled ?? true;
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);
  const requestId = useRef(0);

  const refetch = useCallback(async () => {
    if (!enabled) {
      return;
    }
    const id = ++requestId.current;
    setLoading(true);
    setError(null);
    try {
      const result = await factory();
      if (id === requestId.current) {
        setData(result);
      }
    } catch (caught) {
      if (id === requestId.current) {
        setError(caught instanceof Error ? caught : new Error(String(caught)));
      }
    } finally {
      if (id === requestId.current) {
        setLoading(false);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- caller owns deps
  }, deps);

  useEffect(() => {
    void refetch();
  }, [refetch, enabled]);

  return { data, error, loading, refetch };
}

export function useMutation<TInput, TResult>(
  mutateFn: (input: TInput) => Promise<TResult>,
) {
  const [data, setData] = useState<TResult | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const mutate = useCallback(
    async (input: TInput): Promise<TResult> => {
      setLoading(true);
      setError(null);
      try {
        const result = await mutateFn(input);
        setData(result);
        return result;
      } catch (caught) {
        const next = caught instanceof Error ? caught : new Error(String(caught));
        setError(next);
        throw next;
      } finally {
        setLoading(false);
      }
    },
    [mutateFn],
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { mutate, data, error, loading, reset };
}
