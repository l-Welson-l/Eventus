import React from "react";
import { Link } from "react-router-dom";

export default function RegisterSelect() {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Create an Account</h1>

      <div style={styles.buttonContainer}>
        <Link to="/register/customer" style={styles.customerBtn}>
          Register as Customer
        </Link>

        <Link to="/register/business" style={styles.businessBtn}>
          Register as Business 
        </Link>

        <Link to="/login">
                  login
                </Link>
        
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    gap: "20px",
    alignItems: "center",
    justifyContent: "center",
    background: "#f5f5f5",
    padding: "20px",
  },
  title: { fontSize: "2rem", fontWeight: "bold" },
  buttonContainer: { width: "100%", maxWidth: "400px", display: "flex", flexDirection: "column", gap: "15px" },
  customerBtn: {
    background: "#007bff",
    padding: "12px",
    color: "white",
    textAlign: "center",
    borderRadius: "6px",
    textDecoration: "none",
  },
  businessBtn: {
    background: "#28a745",
    padding: "12px",
    color: "white",
    textAlign: "center",
    borderRadius: "6px",
    textDecoration: "none",
  },
};
