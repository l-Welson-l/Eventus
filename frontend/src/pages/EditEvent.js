import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../api/auth";

const ALL_FEATURES = ["menu", "moments", "community", "users", "leaderboard"];

export default function EditEvent() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("access");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    name: "",
    description: "",
  });

  const [features, setFeatures] = useState({});
  const [originalFeatures, setOriginalFeatures] = useState({});

  useEffect(() => {
    async function loadEvent() {
      try {
        const res = await API.get(`/events/${id}/`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        setForm({
          name: res.data.name,
          description: res.data.description || "",
        });

        const enabled = {};
        (res.data.features || []).forEach((f) => {
          enabled[f.key] = true;
        });

        setFeatures(enabled);
        setOriginalFeatures(enabled);
      } catch {
        alert("Failed to load event");
        navigate("/dashboard");
      } finally {
        setLoading(false);
      }
    }

    loadEvent();
  }, [id, navigate, token]);

  const toggleFeature = (key) => {
    setFeatures((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const saveChanges = async () => {
    try {
      setSaving(true);

      // 1️⃣ Update name / description
      await API.put(
        `/events/${id}/update/`,
        form,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // 2️⃣ Sync features (toggle only changed ones)
      for (const key of ALL_FEATURES) {
        const wasEnabled = !!originalFeatures[key];
        const isEnabled = !!features[key];

        if (wasEnabled !== isEnabled) {
          await API.post(
            `/events/${id}/toggle-feature/`,
            { key },
            { headers: { Authorization: `Bearer ${token}` } }
          );
        }
      }

      alert("Event updated successfully");
      navigate("/dashboard");
    } catch {
      alert("Failed to save changes");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div style={styles.page}>
      <h2>Edit Event</h2>

      {/* BASIC INFO */}
      <div style={styles.card}>
        <label>Name</label>
        <input
          style={styles.input}
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />

        <label>Description</label>
        <textarea
          style={styles.textarea}
          value={form.description}
          onChange={(e) =>
            setForm({ ...form, description: e.target.value })
          }
        />
      </div>

      {/* FEATURES */}
      <div style={styles.card}>
        <h3>Enabled Features</h3>

        {ALL_FEATURES.map((key) => (
          <label key={key} style={styles.featureRow}>
            <input
              type="checkbox"
              checked={!!features[key]}
              onChange={() => toggleFeature(key)}
            />
            {key.charAt(0).toUpperCase() + key.slice(1)}
          </label>
        ))}
      </div>

      {/* ACTIONS */}
      <div style={styles.actions}>
        <button onClick={() => navigate(-1)} style={styles.cancel}>
          Cancel
        </button>

        <button
          onClick={saveChanges}
          disabled={saving}
          style={styles.save}
        >
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </div>
    </div>
  );
}

const styles = {
  page: {
    maxWidth: 600,
    margin: "40px auto",
    fontFamily: "sans-serif",
  },
  card: {
    background: "#fff",
    padding: 20,
    borderRadius: 10,
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
    marginBottom: 20,
  },
  input: {
    width: "100%",
    padding: 10,
    marginBottom: 15,
  },
  textarea: {
    width: "100%",
    minHeight: 80,
    padding: 10,
  },
  featureRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    marginBottom: 8,
  },
  actions: {
    display: "flex",
    justifyContent: "space-between",
  },
  cancel: {
    background: "#ccc",
    border: "none",
    padding: "10px 16px",
    borderRadius: 8,
    cursor: "pointer",
  },
  save: {
    background: "#1a73e8",
    color: "#fff",
    border: "none",
    padding: "10px 16px",
    borderRadius: 8,
    cursor: "pointer",
  },
};
