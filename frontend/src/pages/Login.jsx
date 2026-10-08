import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import api from "../api";
import { HOME, errText, getRole, saveSession } from "../auth";

export default function Login() {
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  if (getRole() && localStorage.getItem("access")) return <Navigate to={HOME[getRole()]} replace />;

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    try {
      const { data } = await api.post("/auth/login/", { username: username.trim(), password });
      saveSession(data);
      navigate(HOME[data.role]);
    } catch (x) {
      setErr(x.response?.status === 401 && !x.response.data?.detail?.includes("approval")
        ? "Invalid username or password." : errText(x));
    }
    setBusy(false);
  };

  const input = "w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-brand focus:ring-2 focus:ring-brand/30";
  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="hidden flex-col justify-center bg-gradient-to-br from-navy via-[#12305a] to-brand/80 p-14 text-white md:flex">
        <p className="mb-3 text-sm font-semibold tracking-widest text-gold">BPUT HACKATHON | TEAM HIRESYNC</p>
        <h1 className="text-5xl font-extrabold">CampusLink</h1>
        <p className="mt-4 max-w-md text-lg text-slate-200">
          AI-powered campus-to-corporate placement management. Profile, match, schedule, track and analyse in one place.
        </p>
        <ul className="mt-8 space-y-2 text-sm text-slate-200">
          <li>Explainable fit scores, not just percentages</li>
          <li>Skill-gap analysis against target roles</li>
          <li>Conflict-free drive scheduling</li>
          <li>Offer tracking and predictive analytics</li>
        </ul>
      </div>
      <div className="flex items-center justify-center p-8">
        <form onSubmit={submit} className="w-full max-w-sm space-y-4">
          <h2 className="text-2xl font-bold text-navy">Sign in</h2>
          <input value={username} onChange={(e) => setU(e.target.value)} placeholder="Username (students: roll number)"
            required autoComplete="username" className={input} />
          <input type="password" value={password} onChange={(e) => setP(e.target.value)} placeholder="Password"
            required autoComplete="current-password" className={input} />
          {err && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{err}</p>}
          <button disabled={busy} className="w-full rounded-xl bg-brand py-3 font-semibold text-white shadow hover:opacity-90 disabled:opacity-60">
            {busy ? "Signing in..." : "Login"}
          </button>
          <p className="border-t border-slate-200 pt-4 text-sm text-slate-600">
            New here? <Link to="/register" className="font-semibold text-brand">Activate student account or register as recruiter</Link>
          </p>
        </form>
      </div>
    </div>
  );
}