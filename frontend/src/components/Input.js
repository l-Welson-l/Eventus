import React from "react";

export default function Input({ label, ...props }) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: "bold" }}>
        {label}
      </label>
      <input
        {...props}
        style={{
          width: "100%",
          padding: "0.6rem",
          border: "1px solid #ccc",
          borderRadius: "4px",
        }}
      />
    </div>
  );
}
