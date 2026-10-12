import { Link } from "react-router-dom";
import { API_BASE_URL } from "../config";

/** Inbox shell — conversation list UI is F2.3. */
export function InboxPage() {
  return (
    <main className="page">
      <h1>Inbox</h1>
      <p className="muted">
        Placeholder. Gateway: <code>{API_BASE_URL}</code>
      </p>
      <nav className="nav">
        <Link to="/login">Login</Link>
        <Link to="/register">Register</Link>
      </nav>
    </main>
  );
}
