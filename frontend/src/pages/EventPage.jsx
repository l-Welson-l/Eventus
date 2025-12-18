// import { useParams } from "react-router-dom";
// import { useEffect, useState } from "react";
// import { getEvent } from "../api/events";

// export default function EventPage() {
//   const { eventId } = useParams();
//   const [event, setEvent] = useState(null);

//   useEffect(() => {
//     const anonId = localStorage.getItem("anonymous_session_id");

//     getEvent(eventId, anonId)
//       .then((res) => setEvent(res.data))
//       .catch(() => alert("Access denied"));
//   }, [eventId]);

//   if (!event) return <p>Loading...</p>;

//   const features = event.features.map((f) => f.key);

//   return (
//     <div>
//       <h1>{event.name}</h1>

//       {features.includes("menu") && <Menu />}
//       {features.includes("moments") && <Moments />}
//       {features.includes("community") && <Community />}
//       {features.includes("users") && <Users />}
//       {features.includes("leaderboard") && <Leaderboard />}
//     </div>
//   );
// }
