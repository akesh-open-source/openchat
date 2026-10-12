import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { isApiError } from "../api";
import { useDevices, useOpenChatApi, useSessions } from "../hooks";
import { formatApiDetail } from "../lib/apiError";
import type { DeviceResponse } from "../types";

function formatWhen(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function deviceLabel(device: DeviceResponse): string {
  const name = device.name?.trim();
  if (name) {
    return name;
  }
  return `Device (${device.client_device_id})`;
}

export function SessionsPage() {
  const navigate = useNavigate();
  const { client } = useOpenChatApi();
  const devices = useDevices();
  const sessions = useSessions();
  const [revokeError, setRevokeError] = useState<string | null>(null);
  const [revokingId, setRevokingId] = useState<string | null>(null);

  const devicesById = useMemo(() => {
    const map = new Map<string, DeviceResponse>();
    for (const device of devices.data ?? []) {
      map.set(device.id, device);
    }
    return map;
  }, [devices.data]);

  useEffect(() => {
    const err = devices.error ?? sessions.error;
    if (isApiError(err) && err.status === 401) {
      client.tokenStore.clear();
      navigate("/login", {
        replace: true,
        state: { from: "/sessions", notice: "Session expired. Please sign in." },
      });
    }
  }, [devices.error, sessions.error, client.tokenStore, navigate]);

  async function onRevoke(sessionId: string) {
    setRevokeError(null);
    setRevokingId(sessionId);
    try {
      await sessions.revokeSession(sessionId);
    } catch (caught) {
      if (isApiError(caught) && caught.status === 401) {
        client.tokenStore.clear();
        navigate("/login", {
          replace: true,
          state: { from: "/sessions", notice: "Session expired. Please sign in." },
        });
        return;
      }
      setRevokeError(formatApiDetail(caught));
    } finally {
      setRevokingId(null);
    }
  }

  const loadError =
    devices.error || sessions.error
      ? formatApiDetail(devices.error ?? sessions.error)
      : null;
  const loading = devices.loading || sessions.loading;

  return (
    <main className="page">
      <h1>Devices & sessions</h1>
      <p className="muted">
        Devices are labeled by name or client device id. You can revoke a session (not a
        device).
      </p>

      {loading && <p className="muted">Loading…</p>}
      {loadError != null && <p className="error">{loadError}</p>}
      {revokeError != null && <p className="error">{revokeError}</p>}

      <section className="panel">
        <h2>Devices</h2>
        {(devices.data ?? []).length === 0 && !devices.loading ? (
          <p className="muted">No devices.</p>
        ) : (
          <ul className="item-list">
            {(devices.data ?? []).map((device) => (
              <li key={device.id}>
                <strong>{deviceLabel(device)}</strong>
                <span className="muted">
                  Last seen {formatWhen(device.last_seen_at)}
                  {device.user_agent ? ` · ${device.user_agent}` : ""}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel">
        <h2>Sessions</h2>
        {(sessions.data ?? []).length === 0 && !sessions.loading ? (
          <p className="muted">No active sessions.</p>
        ) : (
          <ul className="item-list">
            {(sessions.data ?? []).map((session) => {
              const device = devicesById.get(session.device_id);
              const label = device
                ? deviceLabel(device)
                : `Unknown device (${session.device_id.slice(0, 8)}…)`;
              return (
                <li key={session.id}>
                  <div className="item-row">
                    <div>
                      <strong>{label}</strong>
                      <span className="muted">
                        {session.ip_address ?? "No IP"} · last seen{" "}
                        {formatWhen(session.last_seen_at)} · expires{" "}
                        {formatWhen(session.expires_at)}
                      </span>
                    </div>
                    <button
                      type="button"
                      className="button-secondary"
                      disabled={revokingId === session.id}
                      onClick={() => void onRevoke(session.id)}
                    >
                      {revokingId === session.id ? "Revoking…" : "Revoke"}
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <nav className="nav">
        <Link to="/">Inbox</Link>
        <Link to="/change-password">Change password</Link>
      </nav>
    </main>
  );
}
