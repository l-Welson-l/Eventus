import { useEffect, useState } from "react";
import API from "../api/auth";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const [qrPreview, setQrPreview] = useState(null);
  const [user, setUser] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const token = localStorage.getItem("access");

        const userRes = await API.get("/me/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(userRes.data);

        if (userRes.data.user_type === "business") {
          const eventsRes = await API.get("/my-events/", {
            headers: { Authorization: `Bearer ${token}` },
          });
          setEvents(eventsRes.data);
        }
      } catch (err) {
        localStorage.clear();
        window.location.href = "/login";
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) return <p>Loading...</p>;
  if (!user) return null;

  return (
    <div style={styles.page}>
      {/* PROFILE */}
      <div style={styles.profileCard}>
        <div style={styles.avatar}>🏢</div>
        <div>
          <h2>{user.username}</h2>
          <p>{user.email}</p>
        </div>
      </div>

      {/* EVENTS */}
      {user.user_type === "business" && (
        <div style={styles.eventsSection}>
          <h3>Your Events</h3>

          {events.length === 0 ? (
            <button style={styles.createBtn}>
              ➕ Create your first event
            </button>
          ) : (
            <>
              {events.map((e) => (
                <div
                  key={e.id}
                  style={styles.eventCard}
                  onClick={() => (window.location.href = `/events/${e.id}`)}
                >
                  <div>
                    <h4>{e.name}</h4>
                    <p>{e.description || "No description"}</p>
                  </div>

                   <div style={styles.eventActions}>
                      {e.qr_code && (
                        <img
                          src={e.qr_code}
                          alt="QR"
                          style={styles.qrSmall}
                          onClick={(ev) => {
                            ev.stopPropagation();
                            setQrPreview(e.qr_code);
                          }}
                        />
                      )}

                      <button
                        style={styles.editBtn}
                        onClick={(ev) => {
                          ev.stopPropagation();
                          window.location.href = `/events/${e.id}/edit`;
                        }}
                      >
                        ✏️
                      </button>
                    </div>
                </div>
              ))}
              <Link to="/events/create">
                <button style={styles.createBtn}>➕ Create new event</button>
              </Link>
            </>
          )}
        </div>
      )}

      {/* FULLSCREEN QR */}
      {qrPreview && (
        <div
          style={styles.qrOverlay}
          onClick={() => setQrPreview(null)}
        >
          <img src={qrPreview} alt="QR Full" style={styles.qrBig} />
          <p style={{ color: "#fff", marginTop: 10 }}>
            Click to close • Long-press to save/share
          </p>
        </div>
      )}
    </div>
  );
}

const styles = {
  page: {
    padding: 40,
    maxWidth: 900,
    margin: "0 auto",
    fontFamily: "sans-serif",
  },

  profileCard: {
    display: "flex",
    alignItems: "center",
    gap: 20,
    padding: 20,
    borderRadius: 10,
    background: "#fff",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
    marginBottom: 30,
  },

  avatar: {
    width: 70,
    height: 70,
    borderRadius: "50%",
    background: "#e0e0e0",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 32,
  },

  eventsSection: {
    background: "#fff",
    padding: 20,
    borderRadius: 10,
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
  },

  eventCard: {
    padding: 15,
    borderRadius: 8,
    background: "#f5f5f5",
    marginBottom: 10,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    cursor: "pointer",
  },

  qrSmall: {
    width: 60,
    height: 60,
    cursor: "pointer",
  },

  createBtn: {
    marginTop: 15,
    padding: "12px 16px",
    fontSize: 16,
    borderRadius: 8,
    border: "none",
    background: "#1a73e8",
    color: "#fff",
    cursor: "pointer",
  },

  qrOverlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.85)",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },

  qrBig: {
    width: 320,
    height: 320,
    background: "#fff",
    padding: 20,
    borderRadius: 12,
  },
};

