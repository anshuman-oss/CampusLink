import { useEffect, useState } from "react";
import api from "../../api";
import ScoreRing from "../../components/ScoreRing";
import FactorBars from "../../components/FactorBars";

export default function StudentDashboard() {
  const [matches, setMatches] = useState([]);
  const [me, setMe] = useState(null);
  const [offers, setOffers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [role, setRole] = useState("");
  const [gap, setGap] = useState(null);
  const [msg, setMsg] = useState("");
  const load = () => api.get("/students/me/").then((r) => setMe(r.data));
  useEffect(() => {
    load();
    api.get("/students/me/matches/").then((r) => setMatches(r.data));
    api.get("/offers/").then((r) => setOffers(r.data));
    api.get("/students/me/skill-gap/").then((r) => { setRoles(r.data.roles); setRole(r.data.roles[0]); });
  }, []);
  const analyse = async () => setGap((await api.post("/students/me/skill-gap/", { role })).data);
  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData(); fd.append("resume", file);
    setMsg("Reading your resume...");
    try {
      const { data } = await api.post("/students/me/resume/", fd);
      setMsg(`Found ${data.skills.length} skills. Readiness updated to ${data.readiness}.`);
      load();
    } catch { setMsg("Upload failed. Please upload a text-based PDF."); }
  };
  if (!me) return <p>Loading...</p>;
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Welcome, {me.name}</h1>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="font-semibold text-navy">Employability Score</h2>
          <div className="mt-4 flex items-center gap-5">
            <ScoreRing value={me.readiness_score} size={110} />
            <div>
              <p className="text-xl font-bold text-navy">{me.readiness_level}</p>
              <p className="text-xs text-slate-500">{me.branch} | CGPA {me.cgpa} | {me.roll_no}</p>
            </div>
          </div>
          <div className="mt-5"><FactorBars data={me.breakdown} max={25} /></div>
        </div>
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <h2 className="font-semibold text-navy">My skills</h2>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {me.skills.map((s) => <span key={s} className="rounded-md bg-emerald-50 px-2 py-0.5 text-xs text-emerald-700">{s}</span>)}
            </div>
            <label className="mt-4 inline-block cursor-pointer rounded-xl bg-navy px-4 py-2 text-sm font-medium text-white hover:opacity-90">
              Upload resume (PDF)
              <input type="file" accept="application/pdf" onChange={upload} className="hidden" />
            </label>
            {msg && <p className="mt-2 text-sm text-slate-600">{msg}</p>}
          </div>
          <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <h2 className="font-semibold text-navy">Skill-gap analysis</h2>
            <div className="mt-3 flex gap-3">
              <select value={role} onChange={(e) => setRole(e.target.value)} className="rounded-xl border border-slate-300 px-3 py-2 text-sm">
                {roles.map((r) => <option key={r}>{r}</option>)}
              </select>
              <button onClick={analyse} className="rounded-xl bg-brand px-4 py-2 text-sm font-semibold text-white">Analyse</button>
            </div>
            {gap && (
              <div className="mt-4 space-y-3">
                <div className="h-2.5 rounded-full bg-slate-100">
                  <div className="h-2.5 rounded-full bg-brand transition-all duration-700" style={{ width: `${gap.coverage}%` }} />
                </div>
                <p className="text-sm text-slate-600">You cover <b>{gap.coverage}%</b> of the skills for {gap.role}.</p>
                <div className="flex flex-wrap gap-1.5">
                  {gap.have.map((s) => <span key={s} className="rounded-md bg-emerald-50 px-2 py-0.5 text-xs text-emerald-700">{s}</span>)}
                  {gap.missing.map((s) => <span key={s} className="rounded-md bg-rose-50 px-2 py-0.5 text-xs text-rose-700">learn: {s}</span>)}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h2 className="font-semibold text-navy">My offers</h2>
        {offers.length === 0 && <p className="mt-2 text-sm text-slate-500">No offers yet. Keep improving your readiness.</p>}
        {offers.map((o) => (
          <div key={o.id} className="mt-3 flex items-center justify-between rounded-xl bg-slate-50 p-3 text-sm">
            <span><b>{o.company}</b> - {o.job_title} ({o.ctc_lpa} LPA)</span>
            <span className="text-xs capitalize">{o.status} | documents {o.docs_status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}