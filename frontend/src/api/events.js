import API from "./auth";

// Join event (QR scan)
export const joinEvent = (eventId, anonymousSessionId = null) =>
  API.post(`/events/${eventId}/join/`, {
    anonymous_session_id: anonymousSessionId,
  });

// Get event details
export const getEvent = (eventId, anonymousSessionId = null) =>
  API.get(`/events/${eventId}/`, {
    params: { anonymous_session_id: anonymousSessionId },
  });

// Business creates event
export const createEvent = (data) =>
  API.post("/events/create/", data);

// Toggle feature
export const toggleFeature = (eventId, key) =>
  API.post(`/events/${eventId}/toggle-feature/`, { key });
