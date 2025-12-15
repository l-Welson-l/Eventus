import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import API from "../api/auth";

export default function MagicLogin() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [status, setStatus] = useState("");
    const token = searchParams.get("token");

    useEffect(() => {
        if (!token) setStatus("Invalid magic link");
    }, [token]);

    

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!token) return;

        try {
        const res = await API.post("/auth/magic-complete/", {
            token,
            password,
            username,
        });

        localStorage.setItem("access", res.data.access);
        localStorage.setItem("refresh", res.data.refresh);

        setStatus("Account created successfully!");
        setTimeout(() => navigate("/auth-debug"), 1000);
        } catch (err) {
        setStatus("Error completing signup");
        console.error(err);
        }
    };

  return (
    <div style={{ padding: 40 }}>
      <h2>Complete Your Signup</h2>
      {status && <p>{status}</p>}
      {!status.includes("Error") && (
        <form onSubmit={handleSubmit}>
          <label>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </label>
          <br />
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          <br />
          <button type="submit">Complete Signup</button>
        </form>
      )}
    </div>
  );
}
