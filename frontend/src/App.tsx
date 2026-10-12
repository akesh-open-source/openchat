import { Navigate, Route, Routes } from "react-router-dom";
import { InboxPage } from "./pages/InboxPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

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
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
