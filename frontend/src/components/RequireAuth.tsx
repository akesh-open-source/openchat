import { useEffect, useState, type ReactNode } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useOpenChatApi } from "../hooks";

type GateStatus = "checking" | "ok" | "denied";

/**
 * Protects routes using TokenStore only (not a React “isLoggedIn” flag).
 * If access_token is missing but refresh_token exists, tries /auth/refresh once.
 */
export function RequireAuth({ children }: { children?: ReactNode }) {
  const { auth, client } = useOpenChatApi();
  const location = useLocation();
  const [status, setStatus] = useState<GateStatus>("checking");

  useEffect(() => {
    let cancelled = false;

    async function ensureSession() {
      if (client.tokenStore.getAccessToken()) {
        if (!cancelled) {
          setStatus("ok");
        }
        return;
      }

      const refreshToken = client.tokenStore.getRefreshToken();
      if (!refreshToken) {
        if (!cancelled) {
          setStatus("denied");
        }
        return;
      }

      try {
        await auth.refresh();
        if (!cancelled) {
          setStatus(client.tokenStore.getAccessToken() ? "ok" : "denied");
        }
      } catch {
        client.tokenStore.clear();
        if (!cancelled) {
          setStatus("denied");
        }
      }
    }

    setStatus("checking");
    void ensureSession();
    return () => {
      cancelled = true;
    };
  }, [auth, client, location.pathname]);

  if (status === "checking") {
    return (
      <main className="page">
        <p className="muted">Checking session…</p>
      </main>
    );
  }

  if (status === "denied") {
    return (
      <Navigate to="/login" replace state={{ from: location.pathname || "/" }} />
    );
  }

  return children != null ? children : <Outlet />;
}
