import axios from "axios";

const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((c) => {
  const t = localStorage.getItem("access");
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});

api.interceptors.response.use(
  (r) => r,
  (e) => {
    if (e.response?.status === 401 && !e.config.url.includes("/auth/login")) {
      localStorage.clear();
      window.location = "/";
    }
    return Promise.reject(e);
  }
);

export default api;