"use client";

import { useCallback, useEffect, useState } from "react";

type SetStateAction<T> = T | ((prev: T) => T);

type UsePersistentStateReturn<T> = [T, (value: SetStateAction<T>) => void, boolean];

export function usePersistentState<T>(key: string, defaultValue: T): UsePersistentStateReturn<T> {
  const [hydrated, setHydrated] = useState(false);
  const [state, setState] = useState<T>(defaultValue);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const stored = window.localStorage.getItem(key);
    if (stored) {
      try {
        setState(JSON.parse(stored) as T);
      } catch {
        setState(defaultValue);
      }
    } else {
      setState(defaultValue);
    }
    setHydrated(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const updateState = useCallback(
    (value: SetStateAction<T>) => {
      setState((previous) => {
        const nextValue = value instanceof Function ? value(previous) : value;
        if (typeof window !== "undefined") {
          window.localStorage.setItem(key, JSON.stringify(nextValue));
        }
        return nextValue;
      });
    },
    [key],
  );

  return [state, updateState, hydrated];
}
