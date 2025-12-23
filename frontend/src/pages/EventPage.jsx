import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getEvent } from "../api/events";

import Menu from "../components/event/Menu";
import Moments from "../components/event/Moments";
import Community from "../components/event/Community";
import Users from "../components/event/Users";
import Leaderboard from "../components/event/Leaderboard";

import "./EventPage.css";

export default function EventPage() {
  const { eventId } = useParams();
  const [event, setEvent] = useState(null);
  const [activeFeature, setActiveFeature] = useState(null);

  useEffect(() => {
    const anonId = localStorage.getItem("anonymous_session_id");

    getEvent(eventId, anonId)
      .then((res) => setEvent(res.data))
      .catch(() => alert("Access denied"));
  }, [eventId]);

  // Set default feature when event loads
  useEffect(() => {
    if (event?.features?.length) {
      setActiveFeature(event.features[0].key);
    }
  }, [event]);

  if (!event) return <p>Loading...</p>;

  const features = event.features?.map((f) => f.key) || [];

  const renderFeature = () => {
    switch (activeFeature) {
      case "menu":
        return <Menu />;
      case "moments":
        return <Moments />;
      case "community":
        return <Community eventId={eventId} />;
      case "users":
        return <Users />;
      case "leaderboard":
        return <Leaderboard />;
      default:
        return <p>Select a feature</p>;
    }
  };

  return (
    <div className="event-page">
      {/* MAIN CONTENT */}
      <div className="event-content">
        <h2 className="event-title">{event.name}</h2>
        {renderFeature()}
      </div>

      {/* BOTTOM FEATURE BAR */}
      <div className="feature-bar">
        {features.map((key) => (
          <button
            key={key}
            className={`feature-btn ${
              activeFeature === key ? "active" : ""
            }`}
            onClick={() => setActiveFeature(key)}
          >
            {key}
          </button>
        ))}
      </div>
    </div>
  );
}
