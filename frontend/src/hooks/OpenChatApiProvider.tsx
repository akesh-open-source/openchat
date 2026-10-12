import { createContext, useContext, useMemo, type ReactNode } from "react";
import {
  createOpenChatApi,
  LocalStorageTokenStore,
  type OpenChatApi,
} from "../api";
import { API_BASE_URL } from "../config";

const OpenChatApiContext = createContext<OpenChatApi | null>(null);

export interface OpenChatApiProviderProps {
  children: ReactNode;
  /** Defaults to VITE_API_BASE_URL (or http://localhost:8000) with localStorage tokens. */
  api?: OpenChatApi;
  baseUrl?: string;
}

export function OpenChatApiProvider({
  children,
  api,
  baseUrl,
}: OpenChatApiProviderProps) {
  const value = useMemo(
    () =>
      api ??
      createOpenChatApi({
        baseUrl: baseUrl ?? API_BASE_URL,
        tokenStore: new LocalStorageTokenStore(),
      }),
    [api, baseUrl],
  );

  return (
    <OpenChatApiContext.Provider value={value}>{children}</OpenChatApiContext.Provider>
  );
}

export function useOpenChatApi(): OpenChatApi {
  const api = useContext(OpenChatApiContext);
  if (!api) {
    throw new Error("useOpenChatApi must be used inside OpenChatApiProvider");
  }
  return api;
}
