import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import { HOME } from "../App";

const DEMO = [["Officer", "officer"], ["Recruiter", "cloudcorp"], ["Student", "s001"], ["Mentor", "mentor1"]];

export default function Login() {
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [err, setErr] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await api.post("/auth/login/", { username, password });
      localStorage.setItem("access", data.access);
      localStorage.setItem("role", data.role);
      localStorage.setItem("name", data.name);
      navigate(HOME[data.role]);
    } catch {
      setErr("Invalid username or password");
    }
  };

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
          <input value={username} onChange={(e) => setU(e.target.value)} placeholder="Username" required
            className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-brand focus:ring-2 focus:ring-brand/30" />
          <input type="password" value={password} onChange={(e) => setP(e.target.value)} placeholder="Password" required
            className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-brand focus:ring-2 focus:ring-brand/30" />
          {err && <p className="text-sm text-rose-600">{err}</p>}
          <button className="w-full rounded-xl bg-brand py-3 font-semibold text-white shadow hover:opacity-90">Login</button>
          <div className="border-t pt-4">
            <p className="mb-2 text-xs text-slate-500">Demo accounts (password: demo123)</p>
            <div className="flex flex-wrap gap-2">
              {DEMO.map(([label, u]) => (
                <button type="button" key={u} onClick={() => { setU(u); setP("demo123"); }}
                  className="rounded-full bg-slate-100 px-3 py-1 text-xs hover:bg-slate-200">{label}</button>
              ))}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}