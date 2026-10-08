import api from "./api";

export const HOME = { student: "/student", recruiter: "/recruiter", officer: "/officer", mentor: "/officer" };
export const getRole = () => localStorage.getItem("role");

export function saveSession(d) {
  localStorage.setItem("access", d.access);
  localStorage.setItem("refresh", d.refresh);
  localStorage.setItem("role", d.role);
  localStorage.setItem("name", d.name);
}

export async function logout() {
  const refresh = localStorage.getItem("refresh");
  try { if (refresh) await api.post("/auth/logout/", { refresh }); } catch { /* ignore */ }
  localStorage.clear();
}

// Turns any DRF error response into one readable sentence
export function errText(e) {
  const d = e.response?.data;
  if (!d) return "Cannot reach the server. Is the backend running?";
  if (typeof d === "string") return "Server error. Please try again.";
  if (d.detail) return d.detail;
  return Object.entries(d)
    .map(([k, v]) => {
      const msg = [].concat(v).join(" ");
      return k === "non_field_errors" ? msg : `${k.replace("_", " ")}: ${msg}`;
    })
    .join("  |  ");
}