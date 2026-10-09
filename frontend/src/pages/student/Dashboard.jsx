import { useEffect, useState } from "react";
import { Plus, X } from "lucide-react";
import api from "../../api";
import { errText } from "../../auth";
import ScoreRing from "../../components/ScoreRing";
import FactorBars from "../../components/FactorBars";

const input = "rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/30";

function Card({ title, children }) {
  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h2 className="mb-3 font-semibold text-navy">{title}</h2>
      {children}
    </div>
  );
}

const Msg = ({ m }) => m && (
  <p className={`rounded-lg p-3 text-sm ${m.ok ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>{m.t}</p>
);

export default function StudentDashboard() {
  const [me, setMe] = useState(null);
  const [options, setOptions] = useState([]);
  const [skills, setSkills] = useState([]);
  const [certs, setCerts] = useState([]);
  const [projects, setProjects] = useState([]);
  const [newCert, setNewCert] = useState("");
  const [proj, setProj] = useState({ title: "", desc: "" });
  const [offers, setOffers] = useState([]);
  const [matches, setMatches] = useState([]);
  const [roles, setRoles] = useState([]);
  const [role, setRole] = useState("");
  const [gap, setGap] = useState(null);
  const [saveMsg, setSaveMsg] = useState(null);
  const [resumeMsg, setResumeMsg] = useState(null);

  const apply = (d) => {
    setMe(d); setSkills(d.skills); setCerts(d.certifications); setProjects(d.projects);
    if (d.skill_options) setOptions(d.skill_options);
  };
  const load = () => api.get("/students/me/").then((r) => apply(r.data));
  const loadMatches = () => api.get("/students/me/matches/").then((r) => setMatches(r.data));

  useEffect(() => {
    load(); loadMatches();
    api.get("/offers/").then((r) => setOffers(r.data));
    api.get("/students/me/skill-gap/").then((r) => { setRoles(r.data.roles); setRole(r.data.roles[0]); });
  }, []);

  const save = async () => {
    setSaveMsg(null);
    try {
      const { data } = await api.patch("/students/me/", { skills, certifications: certs, projects });
      apply(data); loadMatches();
      setSaveMsg({ ok: true, t: `Saved. Your readiness is now ${data.readiness_score} (${data.readiness_level}) and your matches were refreshed.` });
    } catch (x) { setSaveMsg({ ok: false, t: errText(x) }); }
  };

  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData(); fd.append("resume", file);
    setResumeMsg({ ok: true, t: "Reading your resume..." });
    try {
      const { data } = await api.post("/students/me/resume/", fd);
      setResumeMsg({ ok: true, t: `Found ${data.skills.length} skills in total. Readiness updated to ${data.readiness}.` });
      load(); loadMatches();
    } catch (x) { setResumeMsg({ ok: false, t: errText(x) }); }
    e.target.value = "";
  };

  const analyse = async () => setGap((await api.post("/students/me/skill-gap/", { role })).data);
  const addProject = () => {
    if (!proj.title.trim()) return;
    setProjects([...projects, proj]); setProj({ title: "", desc: "" });
  };
  const addCert = () => {
    if (!newCert.trim()) return;
    setCerts([...certs, newCert.trim()]); setNewCert("");
  };

  if (!me) return <p>Loading...</p>;
  const free = options.filter((o) => !skills.includes(o));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Welcome, {me.name}</h1>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Employability score">
          <div className="flex items-center gap-5">
            <ScoreRing value={me.readiness_score} size={110} />
            <div>
              <p className="text-xl font-bold text-navy">{me.readiness_level}</p>
              <p className="text-xs text-slate-500">{me.branch} | CGPA {me.cgpa} | {me.roll_no}</p>
            </div>
          </div>
          <div className="mt-5"><FactorBars data={me.breakdown} max={25} /></div>
          <p className="mt-4 text-xs text-slate-500">
            Aptitude {me.aptitude_score}, mock interview {me.mock_score} and soft skills {me.soft_score} are entered by the placement cell.
          </p>
        </Card>

        <div className="space-y-6 lg:col-span-2">
          <Card title="My skills, projects and certifications">
            <div className="flex flex-wrap gap-1.5">
              {skills.map((s) => (
                <span key={s} className="flex items-center gap-1 rounded-md bg-emerald-50 px-2 py-1 text-xs text-emerald-700">
                  {s}<button onClick={() => setSkills(skills.filter((x) => x !== s))}><X size={12} /></button>
                </span>
              ))}
              {skills.length === 0 && <p className="text-sm text-slate-400">No skills yet. Add them below or upload your resume.</p>}
            </div>
            <select value="" onChange={(e) => e.target.value && setSkills([...skills, e.target.value])} className={`${input} mt-3`}>
              <option value="">+ Add a skill</option>
              {free.map((o) => <option key={o}>{o}</option>)}
            </select>

            <p className="mt-5 text-xs font-semibold text-slate-500">Projects</p>
            {projects.map((p, i) => (
              <div key={i} className="mt-2 flex items-start justify-between rounded-xl bg-slate-50 p-3 text-sm">
                <span><b>{p.title}</b>{p.desc && <span className="text-slate-600"> - {p.desc}</span>}</span>
                <button onClick={() => setProjects(projects.filter((_, j) => j !== i))}><X size={14} /></button>
              </div>
            ))}
            <div className="mt-2 grid gap-2 md:grid-cols-[1fr_2fr_auto]">
              <input placeholder="Project title" value={proj.title} onChange={(e) => setProj({ ...proj, title: e.target.value })} className={input} />
              <input placeholder="What did you build and which tools did you use?" value={proj.desc} onChange={(e) => setProj({ ...proj, desc: e.target.value })} className={input} />
              <button onClick={addProject} className="rounded-xl bg-slate-100 px-3 hover:bg-slate-200"><Plus size={16} /></button>
            </div>

            <p className="mt-5 text-xs font-semibold text-slate-500">Certifications</p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {certs.map((c, i) => (
                <span key={i} className="flex items-center gap-1 rounded-md bg-violet-50 px-2 py-1 text-xs text-violet-700">
                  {c}<button onClick={() => setCerts(certs.filter((_, j) => j !== i))}><X size={12} /></button>
                </span>
              ))}
            </div>
            <div className="mt-2 flex gap-2">
              <input placeholder="e.g. AWS Cloud Practitioner" value={newCert} onChange={(e) => setNewCert(e.target.value)} className={`${input} flex-1`} />
              <button onClick={addCert} className="rounded-xl bg-slate-100 px-3 hover:bg-slate-200"><Plus size={16} /></button>
            </div>

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <button onClick={save} className="rounded-xl bg-brand px-6 py-2.5 text-sm font-semibold text-white shadow hover:opacity-90">Save changes</button>
              <label className="cursor-pointer rounded-xl bg-navy px-4 py-2.5 text-sm font-medium text-white hover:opacity-90">
                Upload resume (PDF)
                <input type="file" accept="application/pdf" onChange={upload} className="hidden" />
              </label>
            </div>
            <div className="mt-3 space-y-2"><Msg m={saveMsg} /><Msg m={resumeMsg} /></div>
          </Card>

          <Card title="Skill-gap analysis">
            <div className="flex gap-3">
              <select value={role} onChange={(e) => setRole(e.target.value)} className={input}>
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
          </Card>
        </div>
      </div>

      <Card title="Opportunities that match me">
        {matches.length === 0 && <p className="text-sm text-slate-500">No matches yet. They appear when recruiters post jobs and your profile has skills.</p>}
        <div className="grid gap-4 md:grid-cols-2">
          {matches.map((m) => (
            <div key={m.id} className="flex gap-4 rounded-xl bg-slate-50 p-4">
              <ScoreRing value={m.fit_score} />
              <div className="text-sm">
                <p className="font-semibold text-navy">{m.company} - {m.title}</p>
                <p className="text-xs capitalize text-slate-500">{m.status.replace("_", " ")} | {m.ctc_lpa} LPA</p>
                <p className="mt-1 text-xs text-slate-600">{m.explanation.summary}</p>
                {m.explanation.suggestions?.[0] && <p className="mt-1 text-xs text-teal-700">Next step: {m.explanation.suggestions[0]}</p>}
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card title="My offers">
        {offers.length === 0 && <p className="text-sm text-slate-500">No offers yet. Keep improving your readiness.</p>}
        {offers.map((o) => (
          <div key={o.id} className="mt-2 flex items-center justify-between rounded-xl bg-slate-50 p-3 text-sm">
            <span><b>{o.company}</b> - {o.job_title} ({o.ctc_lpa} LPA)</span>
            <span className="text-xs capitalize">{o.status} | documents {o.docs_status}</span>
          </div>
        ))}
      </Card>
    </div>
  );
}