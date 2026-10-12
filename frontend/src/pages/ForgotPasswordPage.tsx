import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks";
import { formatApiDetail } from "../lib/apiError";

export function ForgotPasswordPage() {
  const { forgotPassword, forgotPasswordState } = useAuth();
  const [email, setEmail] = useState("");
  const [detail, setDetail] = useState<string | null>(null);
  const [resetToken, setResetToken] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setDetail(null);
    setResetToken(null);
    try {
      const result = await forgotPassword({ email: email.trim() });
      setDetail(result.detail);
      if (result.reset_token) {
        setResetToken(result.reset_token);
      }
    } catch (caught) {
      setFormError(formatApiDetail(caught));
    }
  }

  const error =
    formError ??
    (forgotPasswordState.error ? formatApiDetail(forgotPasswordState.error) : null);

  return (
    <main className="page">
      <h1>Forgot password</h1>
      <p className="muted">
        Request a reset link from the gateway. The frontend never sends email itself.
      </p>

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

        {error != null && <p className="error">{error}</p>}
        {detail != null && <p className="success">{detail}</p>}
        {resetToken != null && (
          <p className="muted device-id">
            AUTH_DEBUG <code>reset_token</code>: <code>{resetToken}</code>
          </p>
        )}

        <button type="submit" disabled={forgotPasswordState.loading}>
          {forgotPasswordState.loading ? "Sending…" : "Send reset instructions"}
        </button>
      </form>

      {resetToken != null && (
        <p className="nav">
          <Link to={`/reset-password?token=${encodeURIComponent(resetToken)}`}>
            Continue to reset password
          </Link>
        </p>
      )}

      <nav className="nav">
        <Link to="/reset-password">I already have a token</Link>
        <Link to="/login">Login</Link>
      </nav>
    </main>
  );
}
