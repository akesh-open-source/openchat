import { useState } from "react";
import { Link } from "react-router-dom";
import { isApiError } from "../api";
import { useOpenChatApi } from "../hooks";

/** Inbox shell — conversation list UI is F2.3. */
export function InboxPage() {
  const api = useOpenChatApi();
  const [health, setHealth] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function pingGateway() {
    setLoading(true);
    setError(null);
    setHealth(null);
    try {
      const result = await api.auth.health();
      setHealth(result.status);
    } catch (caught) {
      setError(
        isApiError(caught)
          ? `${caught.status}: ${caught.message}`
          : caught instanceof Error
            ? caught.message
            : String(caught),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <h1>Inbox</h1>
      <p className="muted">
        Provider wired. Gateway: <code>{api.client.baseUrl}</code>
      </p>
      <p className="muted">
        Token store:{" "}
        {api.client.tokenStore.getAccessToken() ? "access token present" : "no access token"}
      </p>
      <button type="button" onClick={() => void pingGateway()} disabled={loading}>
        {loading ? "Pinging…" : "GET /health via api.auth"}
      </button>
      {health != null && (
        <p>
          Health: <code>{health}</code>
        </p>
      )}
      {error != null && <p className="error">{error}</p>}
      <nav className="nav">
        <Link to="/login">Login</Link>
        <Link to="/register">Register</Link>
      </nav>
    </main>
  );
}
