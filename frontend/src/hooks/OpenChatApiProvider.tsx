import { createContext, useContext, useMemo, type ReactNode } from "react";
import {
  createOpenChatApi,
  LocalStorageTokenStore,
  type OpenChatApi,
} from "../api";

const OpenChatApiContext = createContext<OpenChatApi | null>(null);

export interface OpenChatApiProviderProps {
  children: ReactNode;
  /** Defaults to a gateway client at http://localhost:8000 with localStorage tokens. */
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
        baseUrl: baseUrl ?? "http://localhost:8000",
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
