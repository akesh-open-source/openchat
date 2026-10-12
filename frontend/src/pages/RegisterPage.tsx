import { Link } from "react-router-dom";

export function RegisterPage() {
  return (
    <main className="page">
      <h1>Register</h1>
      <p className="muted">Two-step register lands in F1.2 — placeholder route only.</p>
      <nav className="nav">
        <Link to="/login">Login</Link>
        <Link to="/">Inbox</Link>
      </nav>
    </main>
  );
}
