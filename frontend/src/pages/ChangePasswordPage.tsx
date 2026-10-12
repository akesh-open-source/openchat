import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { isApiError } from "../api";
import { useAuth, useOpenChatApi } from "../hooks";
import { formatApiDetail } from "../lib/apiError";

export function ChangePasswordPage() {
  const navigate = useNavigate();
  const { client } = useOpenChatApi();
  const { changePassword, changePasswordState } = useAuth();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setSuccess(null);
    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      // Backend revokes all sessions + refresh tokens — clear local store and re-login.
      client.tokenStore.clear();
      setSuccess("Password updated. All sessions were revoked — sign in again.");
      setCurrentPassword("");
      setNewPassword("");
      window.setTimeout(() => {
        navigate("/login", {
          replace: true,
          state: { notice: "Password updated. Please sign in with your new password." },
        });
      }, 1200);
    } catch (caught) {
      if (isApiError(caught) && caught.status === 401) {
        client.tokenStore.clear();
        navigate("/login", {
          replace: true,
          state: { from: "/change-password", notice: "Session expired. Please sign in." },
        });
        return;
      }
      setFormError(formatApiDetail(caught));
    }
  }

  const error =
    formError ??
    (changePasswordState.error ? formatApiDetail(changePasswordState.error) : null);

  return (
    <main className="page">
      <h1>Change password</h1>
      <p className="muted">
        Requires a Bearer access token. Changing password revokes every session on the server.
      </p>

      <form className="form" onSubmit={(e) => void onSubmit(e)}>
        <label className="field">
          <span>Current password</span>
          <input
            type="password"
            name="current_password"
            autoComplete="current-password"
            required
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
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
        {success != null && <p className="success">{success}</p>}

        <button type="submit" disabled={changePasswordState.loading || success != null}>
          {changePasswordState.loading ? "Updating…" : "Update password"}
        </button>
      </form>

      <nav className="nav">
        <Link to="/">Inbox</Link>
        <Link to="/login">Login</Link>
      </nav>
    </main>
  );
}
