import React, { useEffect, useState } from "react";
import API from "../../api/auth";
import "./Moments.css";

export default function Moments({ eventId }) {
  const [moments, setMoments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!eventId) {
      setError("No event selected");
      setLoading(false);
      return;
    }

    const fetchMoments = async () => {
      try {
        const response = await API.get(`events/${eventId}/moments/`);
        // add frontend-only liked_by_me flag
        const enriched = response.data.map(m => ({
          ...m,
          liked_by_me: false,
        }));
        setMoments(enriched);
      } catch (err) {
        console.error(err);
        setError("Failed to load moments.");
      } finally {
        setLoading(false);
      }
    };

    fetchMoments();
  }, [eventId]);

  const toggleLike = async (momentId) => {
  try {
    const res = await API.post(`moments/${momentId}/like/`, {
      anonymous_session_id: anonSessionId // pass if user not logged in
    });
    const { liked, likes_count } = res.data;

    setMoments(prev =>
      prev.map(m =>
        m.id === momentId
          ? { ...m, liked_by_me: liked, likes_count }
          : m
      )
    );
  } catch (err) {
    console.error("Like failed:", err.response?.status, err.response?.data);
  }
};


  if (loading) return <p>Loading moments...</p>;
  if (error) return <p>{error}</p>;
  if (moments.length === 0) return <p>No moments yet for this event.</p>;

  return (
    <section className="moments">
      <h2>Moments</h2>

      {moments.map((moment) => (
        <div key={moment.id} className="moment-card">

          {/* Caption */}
          {moment.caption && <p className="caption">{moment.caption}</p>}

          {/* Media */}
          <div className="moment-media">
            {moment.media.map((media) => {
              const mediaUrl = media.file_url.startsWith("http")
                ? media.file_url
                : `http://localhost:8000${media.file_url}`;

              return (
                <div key={media.id} className="media-item">
                  {media.media_type === "image" ? (
                    <img src={mediaUrl} alt="moment" />
                  ) : (
                    <video controls src={mediaUrl} />
                  )}
                </div>
              );
            })}
          </div>

          {/* Actions */}
          <div className="moment-actions">
            <button
              className={`like-btn ${moment.liked_by_me ? "liked" : ""}`}
              onClick={() => toggleLike(moment.id)}
            >
              ❤️ {moment.likes_count}
            </button>
          </div>

        </div>
      ))}
    </section>
  );

  
}

