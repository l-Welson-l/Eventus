export function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  // keep anon_session if you want magic-link flow to continue
  // localStorage.removeItem("anon_session");

  window.location.href = "/login";
}
