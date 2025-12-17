import React, { useEffect, useState } from "react";
import API from "../api/auth";

export default function AuthDebugPage() {
  const [anonSession, setAnonSession] = useState(
    localStorage.getItem("anon_session")
  );
  const [accessToken, setAccessToken] = useState(
    localStorage.getItem("access")
  );
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  // Keep state in sync with localStorage
  useEffect(() => {
    setAnonSession(localStorage.getItem("anon_session"));
    setAccessToken(localStorage.getItem("access"));
  }, []);

  const requestMagicLink = async () => {
    try {
        const res = await API.post("/auth/magic-link/", {
        email,
        anonymous_session_id: anonSession,
        });

        localStorage.setItem("anon_session", res.data.anonymous_session_id);
        setAnonSession(res.data.anonymous_session_id);
        setMessage("Magic link sent. Check your email.");
    } catch (err) {
        if (err.response?.status === 400) {
        setMessage(err.response.data.detail); // show "account already exists"
        } else {
        setMessage("Error sending magic link");
        }
    }
    };

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setAccessToken(null);
    setMessage("Logged out");
  };

  const clearAnonymous = () => {
    localStorage.removeItem("anon_session");
    setAnonSession(null);
    setMessage("Anonymous session cleared");
  };

  return (
    <div style={{ padding: 40, fontFamily: "sans-serif" }}>
      <h2>Auth Debug Page</h2>

      <hr />

      {/* STATUS */}
      {!accessToken && !anonSession && (
        <p>❌ Not logged in and no anonymous session</p>
      )}

      {!accessToken && anonSession && (
        <p>👤 Anonymous session active</p>
      )}

      {accessToken && (
        <p>✅ Logged in user</p>
      )}

      <hr />

      {/* ACTIONS */}
      {!accessToken && (
        <>
          <input
            placeholder="Email for magic link"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ padding: 8, marginRight: 8 }}
          />
          <button onClick={requestMagicLink}>
            Request Magic Link
          </button>
        </>
      )}

      {accessToken && (
        <button onClick={logout}>
          Logout
        </button>
      )}

      <br /><br />

      <button onClick={clearAnonymous}>
        Clear Anonymous Session
      </button>

      <p style={{ marginTop: 20 }}>{message}</p>

      <hr />

      {/* DEBUG INFO */}
      <pre>
{JSON.stringify(
  {
    anon_session: anonSession,
    access_token_exists: !!accessToken,
  },
  null,
  2
)}
      </pre>
    </div>
  );
}
