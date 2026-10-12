import { useState, type FormEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../hooks";
import { formatApiDetail } from "../lib/apiError";

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { resetPassword, resetPasswordState } = useAuth();

  const [token, setToken] = useState(() => searchParams.get("token") ?? "");
  const [newPassword, setNewPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    try {
      await resetPassword({
        token: token.trim(),
        new_password: newPassword,
      });
      navigate("/login", { replace: true });
    } catch (caught) {
      setFormError(formatApiDetail(caught));
    }
  }

  const error =
    formError ??
    (resetPasswordState.error ? formatApiDetail(resetPasswordState.error) : null);

  return (
    <main className="page">
      <h1>Reset password</h1>
      <p className="muted">
        Enter the reset token and a new password. This route is public (no Bearer).
      </p>

      <form className="form" onSubmit={(e) => void onSubmit(e)}>
        <label className="field">
          <span>Reset token</span>
          <input
            type="text"
            name="token"
            required
            autoComplete="one-time-code"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
        </label>

        <label className="field">
          <span>New password</span>
          <input
            type="password"
            name="new_password"
            autoComplete="new-password"
            required
            minLength={8}
            maxLength={128}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
        </label>

        {error != null && <p className="error">{error}</p>}

        <button type="submit" disabled={resetPasswordState.loading || !token.trim()}>
          {resetPasswordState.loading ? "Updating…" : "Reset password"}
        </button>
      </form>

      <nav className="nav">
        <Link to="/forgot-password">Forgot password</Link>
        <Link to="/login">Login</Link>
      </nav>
    </main>
  );
}
