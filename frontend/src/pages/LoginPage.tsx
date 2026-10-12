import { Link } from "react-router-dom";

export function LoginPage() {
  return (
    <main className="page">
      <h1>Login</h1>
      <p className="muted">Auth UI lands in F1.1 — placeholder route only.</p>
      <nav className="nav">
        <Link to="/register">Register</Link>
        <Link to="/">Inbox</Link>
      </nav>
    </main>
  );
}
