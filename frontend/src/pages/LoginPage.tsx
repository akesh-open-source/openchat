import { useMemo, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { isApiError } from "../api";
import { useAuth } from "../hooks";
import { getOrCreateDeviceId } from "../lib/deviceId";

function formatApiDetail(error: unknown): string {
  if (isApiError(error)) {
    const detail = error.body?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (detail != null) {
      return JSON.stringify(detail);
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

export function LoginPage() {
  const navigate = useNavigate();
  const { login, loginState } = useAuth();
  const deviceId = useMemo(() => getOrCreateDeviceId(), []);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [deviceName, setDeviceName] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    try {
      await login({
        email: email.trim(),
        password,
        device_id: deviceId,
        device_name: deviceName.trim() || null,
      });
      navigate("/", { replace: true });
    } catch (caught) {
      setFormError(formatApiDetail(caught));
    }
  }

  const error = formError ?? (loginState.error ? formatApiDetail(loginState.error) : null);

  return (
    <main className="page">
      <h1>Login</h1>
      <p className="muted">Sign in via the gateway. Tokens go to LocalStorageTokenStore.</p>

      <form className="form" onSubmit={(e) => void onSubmit(e)}>
        <label className="field">
          <span>Email</span>
          <input
            type="email"
            name="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            name="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        <label className="field">
          <span>Device name (optional)</span>
          <input
            type="text"
            name="device_name"
            maxLength={120}
            placeholder="e.g. Browser on laptop"
            value={deviceName}
            onChange={(e) => setDeviceName(e.target.value)}
          />
        </label>

        <p className="muted device-id">
          device_id: <code>{deviceId}</code>
        </p>

        {error != null && <p className="error">{error}</p>}

        <button type="submit" disabled={loginState.loading}>
          {loginState.loading ? "Signing in…" : "Sign in"}
        </button>
      </form>

      <nav className="nav">
        <Link to="/register">Register</Link>
        <Link to="/">Inbox</Link>
      </nav>
    </main>
  );
}
