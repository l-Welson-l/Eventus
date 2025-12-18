import { useParams, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { joinEvent } from "../api/events";

export default function EventJoin() {
  const { eventId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const anonId = localStorage.getItem("anonymous_session_id");

    joinEvent(eventId, anonId)
      .then(() => {
        navigate(`/event/${eventId}`);
      })
      .catch(() => {
        alert("Failed to join event");
      });
  }, [eventId]);

  return <p>Joining event...</p>;
}
