import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth, useOpenChatApi } from "../hooks";
import { formatApiDetail } from "../lib/apiError";

/** Inbox shell — conversation list UI is F2.3. */
export function InboxPage() {
  const api = useOpenChatApi();
  const { isAuthenticated, logout, logoutState } = useAuth();
  const [meLabel, setMeLabel] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadMe() {
    setLoading(true);
    setError(null);
    setMeLabel(null);
    try {
      const profile = await api.users.getMe();
      setMeLabel(
        profile.email
          ? `${profile.display_name} <${profile.email}>`
          : profile.display_name,
      );
    } catch (caught) {
      setError(formatApiDetail(caught));
    } finally {
      setLoading(false);
    }
  }

  async function onLogout() {
    setError(null);
    setMeLabel(null);
    try {
      await logout();
    } catch (caught) {
      setError(formatApiDetail(caught));
    }
  }

  return (
    <main className="page">
      <h1>Inbox</h1>
      <p className="muted">
        Gateway: <code>{api.client.baseUrl}</code>
      </p>
      <p className="muted">
        {isAuthenticated ? "Signed in (access token present)" : "Not signed in"}
      </p>

      <div className="row">
        <button type="button" onClick={() => void loadMe()} disabled={loading || !isAuthenticated}>
          {loading ? "Loading…" : "GET /users/me"}
        </button>
        {isAuthenticated && (
          <button type="button" onClick={() => void onLogout()} disabled={logoutState.loading}>
            {logoutState.loading ? "Signing out…" : "Logout"}
          </button>
        )}
      </div>

      {meLabel != null && (
        <p>
          Me: <code>{meLabel}</code>
        </p>
      )}
      {error != null && <p className="error">{error}</p>}

      <nav className="nav">
        {isAuthenticated ? (
          <Link to="/change-password">Change password</Link>
        ) : (
          <Link to="/login">Login</Link>
        )}
        <Link to="/register">Register</Link>
      </nav>
    </main>
  );
}
