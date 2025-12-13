import React, { useState } from "react";
import Input from "../components/Input";
import { registerUser } from "../api/auth";

export default function RegisterBusiness() {
  const [form, setForm] = useState({
    email: "",
    business_name: "",
    address: "",
    password1: "",
    password2: "",
    user_type: "business",
    username: "", // auto-fill
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // auto-set username to business_name
    form.username = form.business_name;

    try {
      await registerUser(form);
      setSuccess("Business account created!");
    } catch (err) {
      setError(JSON.stringify(err.response?.data || "Error"));
    }
  };

  return (
    <div style={styles.container}>
      <form style={styles.form} onSubmit={handleSubmit}>
        <h2>Business Registration</h2>

        {error && <p style={{ color: "red" }}>{error}</p>}
        {success && <p style={{ color: "green" }}>{success}</p>}

        <Input
          label="Business Name"
          value={form.business_name}
          onChange={(e) => setForm({ ...form, business_name: e.target.value })}
        />

        <Input
          label="Address"
          value={form.address}
          onChange={(e) => setForm({ ...form, address: e.target.value })}
        />

        <Input
          label="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />

        <Input
          label="Password"
          type="password"
          value={form.password1}
          onChange={(e) => setForm({ ...form, password1: e.target.value })}
        />

        <Input
          label="Confirm Password"
          type="password"
          value={form.password2}
          onChange={(e) => setForm({ ...form, password2: e.target.value })}
        />

        <button style={styles.button}>Register Business</button>
      </form>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f5f5f5",
  },
  form: {
    background: "#fff",
    padding: "20px",
    borderRadius: "8px",
    width: "100%",
    maxWidth: "400px",
    boxShadow: "0 0 10px rgba(0,0,0,0.1)",
  },
  button: {
    width: "100%",
    padding: "10px",
    background: "#28a745",
    color: "#fff",
    borderRadius: "4px",
    border: "none",
    cursor: "pointer",
    marginTop: "15px",
  },
};
