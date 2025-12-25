import React, { useEffect, useState } from "react";
import API from "../../api/auth";

export default function CommunityPage({ eventId }) {
  const [posts, setPosts] = useState([]);
  const [text, setText] = useState("");
  const [image, setImage] = useState(null);

  const [showAnonModal, setShowAnonModal] = useState(false);
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState("");

  /* -----------------------------
     LOAD POSTS (polling = realtime-ish)
  ------------------------------ */
  useEffect(() => {
    fetchPosts();
    const interval = setInterval(fetchPosts, 3000);
    return () => clearInterval(interval);
  }, [eventId]);

  const fetchPosts = async () => {
    try {
      const res = await API.get(`/events/${eventId}/posts/`);
      setPosts(res.data);
    } catch (err) {
      console.error("Failed to fetch posts");
    }
  };

  /* -----------------------------
     SOFT GATE ON PAGE LOAD
  ------------------------------ */
  useEffect(() => {
    const access = localStorage.getItem("access");
    const anon = localStorage.getItem("anonymous_session_id");
    const dismissed = localStorage.getItem("anon_prompt_dismissed");

    if (!access && !anon && !dismissed) {
      setShowAnonModal(true);
    }
  }, []);

  /* -----------------------------
     POST HANDLERS
  ------------------------------ */
  const submitPost = async () => {
    if (!text && !image) return;

    const access = localStorage.getItem("access");
    const anon = localStorage.getItem("anonymous_session_id");

    // HARD GATE
    if (!access && !anon) {
      setShowAnonModal(true);
      return;
    }

    await actuallySubmitPost();
  };

  const actuallySubmitPost = async () => {
    const formData = new FormData();
    formData.append("text", text);
    if (image) formData.append("image", image);

    const anonId = localStorage.getItem("anonymous_session_id");
    if (anonId) formData.append("anonymous_session_id", anonId);

    try {
      await API.post(
        `/events/${eventId}/posts/`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setText("");
      setImage(null);
      fetchPosts();
    } catch (err) {
      console.error("Post failed");
    }
  };

  /* -----------------------------
     ANON EMAIL SUBMIT
  ------------------------------ */
  const submitAnonEmail = async () => {
    setEmailError("");

    if (!email.includes("@")) {
      setEmailError("Enter a valid email");
      return;
    }

    try {
      const res = await API.post("/auth/magic-link/", {
        email,
        anonymous_session_id: null,
      });

      localStorage.setItem(
        "anonymous_session_id",
        res.data.anonymous_session_id
      );
      localStorage.removeItem("anon_prompt_dismissed");

      setShowAnonModal(false);
      setEmail("");

      setTimeout(actuallySubmitPost, 200);
    } catch (err) {
      setEmailError(
        err.response?.data?.detail || "Failed to send email"
      );
    }
  };

  /* -----------------------------
     UI
  ------------------------------ */
  return (
    <div style={{ padding: 20 }}>

      <h2>Community</h2>

      {/* CREATE POST */}
      <div style={{ marginBottom: 20 }}>
        <textarea
          placeholder="Write something..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={{ width: "100%", padding: 10 }}
        />

        <input
          type="file"
          onChange={(e) => setImage(e.target.files[0])}
        />

        <button onClick={submitPost} style={{ marginTop: 10 }}>
          Post
        </button>
      </div>

      {/* POSTS */}
      {posts.map((post) => (
        <div
          key={post.id}
          style={{
            border: "1px solid #ddd",
            padding: 10,
            marginBottom: 10,
            borderRadius: 6,
          }}
        >
          <small style={{ color: "#666" }}>
            {post.author_name}
          </small>

          <p>{post.text}</p>

          {post.image && (
            <img
              src={post.image}
              alt=""
              style={{ maxWidth: "100%", borderRadius: 6 }}
            />
          )}
        </div>
      ))}

      {/* ANON MODAL */}
      {showAnonModal && (
        <div style={modalOverlay}>
          <div style={modalBox}>
            <h3>Enter your email</h3>
            <p>You need an email to post.</p>

            <input
              type="email"
              placeholder="you@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ width: "100%", padding: 8 }}
            />

            {emailError && (
              <p style={{ color: "red" }}>{emailError}</p>
            )}

            <div style={{ marginTop: 10 }}>
              <button onClick={submitAnonEmail}>
                Continue
              </button>

              <button
                style={{ marginLeft: 10 }}
                onClick={() => {
                  localStorage.setItem(
                    "anon_prompt_dismissed",
                    "true"
                  );
                  setShowAnonModal(false);
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* -----------------------------
   STYLES
------------------------------ */
const modalOverlay = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.4)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1000,
};

const modalBox = {
  background: "#fff",
  padding: 20,
  borderRadius: 8,
  width: 300,
};
