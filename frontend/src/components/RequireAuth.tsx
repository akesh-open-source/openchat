import { Navigate, useLocation } from "react-router-dom";
import { useOpenChatApi } from "../hooks";
import type { ReactNode } from "react";

/** Redirects to /login when TokenStore has no access token. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { client } = useOpenChatApi();
  const location = useLocation();
  const token = client.tokenStore.getAccessToken();

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return children;
}
