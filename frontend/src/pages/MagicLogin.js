import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import API from "../api/auth";

export default function MagicLogin() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState("Verifying magic link...");

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      setStatus("Invalid magic link");
      return;
    }

    API.post("/auth/magic-verify/", { token })
      .then((res) => {
        // Save tokens
        localStorage.setItem("access", res.data.access);
        localStorage.setItem("refresh", res.data.refresh);

        // Anonymous session no longer needed
        localStorage.removeItem("anon_session");
        localStorage.removeItem("display_name");

        setStatus("Logged in successfully!");

        // Redirect after short delay
        setTimeout(() => navigate("/auth-debug"), 1000);
      })
      .catch(() => {
        setStatus("Magic link invalid or expired");
      });
  }, [navigate, searchParams]);

  return (
    <div style={{ padding: 40 }}>
      <h2>{status}</h2>
    </div>
  );
}
