import axios from "axios";

const api = axios.create({ baseURL: "/api" });
let refreshing = null;   // shared promise so parallel requests refresh only once

api.interceptors.request.use((c) => {
  const t = localStorage.getItem("access");
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});

function forceLogout() {
  localStorage.clear();
  window.location.href = "/";
}

api.interceptors.response.use(
  (r) => r,
  async (e) => {
    const orig = e.config;
    const isAuthCall = ["/auth/login", "/auth/refresh", "/auth/register", "/auth/logout"].some((u) =>
      orig?.url?.includes(u)
    );
    if (e.response?.status === 401 && !orig._retry && !isAuthCall) {
      const refresh = localStorage.getItem("refresh");
      if (!refresh) { forceLogout(); return Promise.reject(e); }
      orig._retry = true;
      try {
        refreshing = refreshing || axios.post("/api/auth/refresh/", { refresh }).finally(() => { refreshing = null; });
        const { data } = await refreshing;
        localStorage.setItem("access", data.access);
        if (data.refresh) localStorage.setItem("refresh", data.refresh);   // rotated token
        orig.headers.Authorization = `Bearer ${data.access}`;
        return api(orig);                                                  // retry the failed request
      } catch {
        forceLogout();
      }
    }
    return Promise.reject(e);
  }
);

export default api;