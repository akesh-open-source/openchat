import { Navigate, Route, Routes } from "react-router-dom";
import { RequireAuth } from "./components/RequireAuth";
import { ChangePasswordPage } from "./pages/ChangePasswordPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { InboxPage } from "./pages/InboxPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { SessionsPage } from "./pages/SessionsPage";

export function App() {
  return (
    <div className="app">
      <header className="app-header">
        <strong>OpenChat</strong>
        <span className="muted">frontend scaffold</span>
      </header>
      <Routes>
        <Route path="/" element={<InboxPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route
          path="/change-password"
          element={
            <RequireAuth>
              <ChangePasswordPage />
            </RequireAuth>
          }
        />
        <Route
          path="/sessions"
          element={
            <RequireAuth>
              <SessionsPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
