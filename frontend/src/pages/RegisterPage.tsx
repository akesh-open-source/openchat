import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks";
import { formatApiDetail } from "../lib/apiError";

type Step = "initiate" | "complete" | "done";

export function RegisterPage() {
  const { initiateRegister, completeRegister, registerState } = useAuth();
  const initiate = registerState.initiateRegister;
  const complete = registerState.completeRegister;

  const [step, setStep] = useState<Step>("initiate");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [token, setToken] = useState("");
  const [initiateDetail, setInitiateDetail] = useState<string | null>(null);
  const [debugTokenShown, setDebugTokenShown] = useState(false);
  const [completedEmail, setCompletedEmail] = useState<string | null>(null);
  const [completedName, setCompletedName] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  async function onInitiate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setInitiateDetail(null);
    setDebugTokenShown(false);
    try {
      const result = await initiateRegister({
        email: email.trim(),
        password,
        display_name: displayName.trim(),
      });
      setInitiateDetail(result.detail);
      if (result.registration_token) {
        setToken(result.registration_token);
        setDebugTokenShown(true);
      }
      setStep("complete");
    } catch (caught) {
      setFormError(formatApiDetail(caught));
    }
  }

  async function onComplete(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    try {
      const result = await completeRegister({ token: token.trim() });
      setCompletedEmail(result.email);
      setCompletedName(result.display_name);
      setStep("done");
    } catch (caught) {
      setFormError(formatApiDetail(caught));
    }
  }

  const error =
    formError ??
    (step === "initiate" && initiate.error
      ? formatApiDetail(initiate.error)
      : step === "complete" && complete.error
        ? formatApiDetail(complete.error)
        : null);

  return (
    <main className="page">
      <h1>Register</h1>
      <p className="muted">
        Two steps: initiate, then complete with the email (or debug) token. Complete does not
        return session tokens, so sign in after.
      </p>

      {step === "initiate" && (
        <form className="form" onSubmit={(e) => void onInitiate(e)}>
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
              autoComplete="new-password"
              required
              minLength={8}
              maxLength={128}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          <label className="field">
            <span>Display name</span>
            <input
              type="text"
              name="display_name"
              autoComplete="nickname"
              required
              minLength={3}
              maxLength={30}
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </label>

          {error != null && <p className="error">{error}</p>}

          <button type="submit" disabled={initiate.loading}>
            {initiate.loading ? "Sending…" : "Continue"}
          </button>
        </form>
      )}

      {step === "complete" && (
        <>
          {initiateDetail != null && <p className="success">{initiateDetail}</p>}
          {debugTokenShown && (
            <p className="muted">
              AUTH_DEBUG returned a <code>registration_token</code> — prefilled below for local
              testing.
            </p>
          )}
          {!debugTokenShown && (
            <p className="muted">
              Paste the registration token from your email (or leave blank until you have it).
            </p>
          )}

          <form className="form" onSubmit={(e) => void onComplete(e)}>
            <label className="field">
              <span>Registration token</span>
              <input
                type="text"
                name="token"
                required
                autoComplete="one-time-code"
                value={token}
                onChange={(e) => setToken(e.target.value)}
              />
            </label>

            {error != null && <p className="error">{error}</p>}

            <div className="row">
              <button type="submit" disabled={complete.loading || !token.trim()}>
                {complete.loading ? "Completing…" : "Complete registration"}
              </button>
              <button
                type="button"
                className="button-secondary"
                onClick={() => {
                  setFormError(null);
                  setStep("initiate");
                }}
              >
                Back
              </button>
            </div>
          </form>
        </>
      )}

      {step === "done" && (
        <div className="form">
          <p className="success">
            Account created for{" "}
            <strong>
              {completedName} ({completedEmail})
            </strong>
            . Sign in to get a session — complete-register does not issue tokens.
          </p>
          <Link className="button-link" to={`/login?email=${encodeURIComponent(completedEmail ?? "")}`}>
            Go to login
          </Link>
        </div>
      )}

      <nav className="nav">
        <Link to="/login">Login</Link>
        <Link to="/">Inbox</Link>
      </nav>
    </main>
  );
}
