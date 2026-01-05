import React, { useEffect, useState } from "react";
import API from "../../api/auth";

export default function CommunityPage({ eventId, onOpenPost }) {
  const [posts, setPosts] = useState([]);
  const [text, setText] = useState("");
  const [subtopic, setSubtopic] = useState("");
  const [subtopics, setSubtopics] = useState([]);
  const [activePost, setActivePost] = useState(null);
  const [comments, setComments] = useState([]);
const [email, setEmail] = useState("");
const [emailError, setEmailError] = useState("");
const [pendingAction, setPendingAction] = useState(null);
const [commentText, setCommentText] = useState(""); 


  const [showAnonModal, setShowAnonModal] = useState(false);

  useEffect(() => {
    const access = localStorage.getItem("access");
    const anon = localStorage.getItem("anonymous_session_id");
    const dismissed = localStorage.getItem("anon_prompt_dismissed");

    if (!access && !anon && !dismissed) {
        setShowAnonModal(true);
    }
}, []);


  useEffect(() => {
    fetchPosts();
    fetchSubtopics();
  }, [eventId]);

  const fetchPosts = async () => {
    const res = await API.get(`/events/${eventId}/posts/`);
    setPosts(res.data);
  };

  const fetchSubtopics = async () => {
    const res = await API.get(`/events/${eventId}/subtopics/`);
    setSubtopics(res.data);
  };

    const submitPost = async () => {
        const access = localStorage.getItem("access");
        const anon = localStorage.getItem("anonymous_session_id");

        // 🔒 HARD GATE FIRST
        if (!access && !anon) {
            setPendingAction("post");
            setShowAnonModal(true);
            return;
        }

        // ✅ THEN validate
        if (!text || !subtopic) return;

        await API.post(`/events/${eventId}/posts/`, {
            text,
            subtopic,
            anonymous_session_id: anon,
        });

        setText("");
        setSubtopic("");
        fetchPosts();
    };
    const submitComment = async () => {
        if (!commentText.trim()) return;

        const access = localStorage.getItem("access");
        const anon = localStorage.getItem("anonymous_session_id");

        if (!access && !anon) {
            setPendingAction("comment");
            setShowAnonModal(true);
            return;
        }

        try {
            await API.post(`/posts/${activePost.id}/comments/create/`, {
            text: commentText,
            anonymous_session_id: anon,
            });

            setCommentText("");

            const res = await API.get(`/posts/${activePost.id}/comments/`);
            setComments(res.data);
        } catch (err) {
            console.error("Failed to submit comment");
        }
    };


    const openPost = async (post) => {
        setActivePost(post);

        try {
            const res = await API.get(`/posts/${post.id}/comments/`);
            setComments(res.data);
        } catch (err) {
            console.error("Failed to load comments");
        }
    };
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

            // retry the blocked action
            setTimeout(() => {
            if (pendingAction === "post") submitPost();
            if (pendingAction === "comment") submitComment();
            setPendingAction(null);
            }, 200);
        } catch (err) {
            setEmailError(
            err.response?.data?.detail || "Failed to send email"
            );
        }
    };

    const likePost = async (postId) => {
        
        const anon = localStorage.getItem("anonymous_session_id");

        try {
            await API.post(`/posts/${postId}/like/`, {
            anonymous_session_id: anon,
            });
            fetchPosts(); // refresh counts
        } catch (err) {
            setShowAnonModal(true);
        }
    };

    const likeComment = async (commentId) => {
        const anon = localStorage.getItem("anonymous_session_id");

        await API.post(`/comments/${commentId}/like/`, {
            anonymous_session_id: anon,
        });

        openPost(activePost); // reload comments
    };



  return (
    <div style={{ padding: 20 }}>
    <h2>Discussions</h2>

    {!activePost && (
        <>
        {/* CREATE POST */}
        <div style={{ marginBottom: 20 }}>
            <select
            value={subtopic}
            onChange={(e) => setSubtopic(e.target.value)}
            style={{ width: "100%", padding: 8 }}
            >
            <option value="">Select topic</option>
            {subtopics.map((s) => (
                <option key={s.id} value={s.id}>
                {s.title}
                </option>
            ))}
            </select>

            <textarea
            placeholder="Start a discussion..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            style={{ width: "100%", padding: 10, marginTop: 10 }}
            />

            <button onClick={submitPost} style={{ marginTop: 10 }}>
            Post
            </button>
        </div>

        {/* POSTS LIST */}
        {posts.map((post) => (
            <div
            key={post.id}
            onClick={() => openPost(post)}
            style={{
                border: "1px solid #ddd",
                padding: 12,
                marginBottom: 10,
                borderRadius: 6,
                cursor: "pointer",
            }}
            >
            <strong>{post.subtopic_title}</strong>
            <small>{post.author_name}</small>
            <p>{post.text}</p>
            <button
                onClick={(e) => {
                    e.stopPropagation();
                    likePost(post.id);
                }}
                >
                ❤️ {post.like_count}
            </button>

            <small style={{ color: "#666" }}>
                {post.comment_count} comments
            </small>
            </div>
        ))}
        </>
    )}

    {activePost && (
        <div>
        <button
            onClick={() => {
            setActivePost(null);
            setComments([]);
            }}
        >
            ← Back
        </button>

        <h3>{activePost.subtopic_title}</h3>
        <p>{activePost.text}</p>

        <small style={{ color: "#666" }}>
            {activePost.author_name}
        </small>

        <hr />

        {/* COMMENTS */}
        {comments.length === 0 ? (
            <p style={{ color: "#999" }}>No comments yet</p>
        ) : (
            comments.map((c) => (
            <div key={c.id} style={{ marginBottom: 10 }}>
                <small style={{ fontWeight: "bold" }}>
                {c.author_name}
                </small>
                <p>{c.text}</p>
                <button onClick={() => likeComment(c.id)}>
                    ❤️ {c.like_count}
                </button>
            </div>
            ))
        )}

        {/* ADD COMMENT */}
        <textarea
            placeholder="Write a comment..."
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            style={{ width: "100%", padding: 8 }}
        />

        <button onClick={submitComment}>
            Comment
        </button>
        </div>
    )}
    {showAnonModal && (
        <div style={modalOverlay}>
            <div style={modalBox}>
            <h3>Enter your email</h3>
            <p>You need an email to post or comment.</p>

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
