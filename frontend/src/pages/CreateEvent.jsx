import { useState } from "react";
import { createEvent } from "../api/events";

export default function CreateEvent() {
  const [name, setName] = useState("");
  const [features, setFeatures] = useState([]);

  const toggleFeature = (key) => {
    setFeatures((prev) =>
      prev.includes(key)
        ? prev.filter((f) => f !== key)
        : [...prev, key]
    );
  };

  const submit = () => {
    createEvent({ name, features }).then((res) => {
      alert("Event created!");
    });
  };

  return (
    <div>
      <h2>Create Event</h2>
      <input onChange={(e) => setName(e.target.value)} placeholder="Event name" />

      {["menu", "moments", "community", "users", "leaderboard"].map((f) => (
        <label key={f}>
          <input
            type="checkbox"
            onChange={() => toggleFeature(f)}
          />
          {f}
        </label>
      ))}

      <button onClick={submit}>Create</button>
    </div>
  );
}
