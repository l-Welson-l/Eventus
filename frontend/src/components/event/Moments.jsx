import React, { useEffect, useState } from "react";
import axios from "axios";

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
        const response = await axios.get(
          `http://localhost:8000/api/events/${eventId}/moments/`
        );
        setMoments(response.data);
      } catch (err) {
        console.error(err);
        setError("Failed to load moments. Make sure the event exists.");
      } finally {
        setLoading(false);
      }
    };

    fetchMoments();
  }, [eventId]);

  if (loading) return <p>Loading moments...</p>;
  if (error) return <p>{error}</p>;
  if (moments.length === 0) return <p>No moments yet for this event.</p>;

  return (
    <section className="moments">
      <h2>Moments</h2>
      {moments.map((moment) => (
        <div key={moment.id} className="moment-card">
          {moment.caption && <p>{moment.caption}</p>}
          <div className="moment-media">
            {moment.media.map((media) => {
              const mediaUrl = media.file_url.startsWith("http")
                ? media.file_url
                : `http://localhost:8000${media.file_url}`;

              return (
                <div key={media.id} className="media-item">
                  {media.media_type === "image" ? (
                    <img
                      src={mediaUrl}
                      alt={`Moment ${moment.id}`}
                      style={{ maxWidth: "200px", marginRight: "10px" }}
                    />
                  ) : (
                    <video
                      controls
                      src={mediaUrl}
                      style={{ maxWidth: "200px", marginRight: "10px" }}
                    />
                  )}
                </div>
              );
            })}
          </div>
          <p>Likes: {moment.likes_count}</p>
        </div>
      ))}
    </section>
  );
}
