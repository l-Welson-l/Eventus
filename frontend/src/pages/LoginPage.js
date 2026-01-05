import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/auth";
import { Link } from "react-router-dom";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

//   useEffect(() => {
//         if (localStorage.getItem("access")) {
//             navigate("/");
//         }
//     }, [navigate]);

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post("login/", form);
      localStorage.setItem("access", res.data.tokens.access);
      localStorage.setItem("refresh", res.data.tokens.refresh);
      navigate("/dashboard");
    } catch (err) {
        if (err.response?.status === 403) {
            setMessage("Please verify your email first.");
        } else {
            setMessage("Invalid credentials or server error.");
        }
    }

  };

  return (
    <div className="auth-container">
      <h2>Login</h2>

      {/* Normal login form */}
      <form onSubmit={handleSubmit}>
        <input
          name="email"
          placeholder="Email"
          onChange={handleChange}
        />
        <input
          name="password"
          type="password"
          placeholder="Password"
          onChange={handleChange}
        />
        <button type="submit">Login</button>
      </form>
      

      <hr />
      <Link to="/">
          Register
        </Link>

      <p>{message}</p>
    </div>
  );
}