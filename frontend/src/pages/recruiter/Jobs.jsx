import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../api";

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [f, setF] = useState({ title: "", description: "", ctc_lpa: "" });
  const [err, setErr] = useState("");
  const navigate = useNavigate();
  const canPost = localStorage.getItem("role") === "recruiter";
  useEffect(() => { api.get("/jobs/").then((r) => setJobs(r.data)); }, []);
  const create = async (e) => {
    e.preventDefault();
    try {
      const { data } = await api.post("/jobs/", { ...f, ctc_lpa: f.ctc_lpa || 0 });
      navigate(`/recruiter/jobs/${data.id}`);
    } catch (x) {
      setErr(JSON.stringify(x.response?.data || "Could not create job"));
    }
  };
  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-navy">Job Descriptions</h1>
      {canPost && (
        <form onSubmit={create} className="space-y-3 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="font-semibold text-navy">Post a new job - the AI reads the description for you</h2>
          <div className="grid gap-3 md:grid-cols-3">
            <input required placeholder="Job title" value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })}
              className="rounded-xl border border-slate-300 px-4 py-2.5 md:col-span-2" />
            <input placeholder="CTC (LPA)" type="number" step="0.1" value={f.ctc_lpa}
              onChange={(e) => setF({ ...f, ctc_lpa: e.target.value })} className="rounded-xl border border-slate-300 px-4 py-2.5" />
          </div>
          <textarea required rows={4} value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })}
            placeholder="Paste the job description. Example: Looking for Python, Django, SQL and Git skills. Minimum CGPA 7.0, no backlogs. CSE and IT."
            className="w-full rounded-xl border border-slate-300 px-4 py-2.5" />
          {err && <p className="text-sm text-rose-600">{err}</p>}
          <button className="rounded-xl bg-brand px-6 py-2.5 font-semibold text-white shadow hover:opacity-90">Analyse and Post</button>
        </form>
      )}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {jobs.map((j) => (
          <Link key={j.id} to={`/recruiter/jobs/${j.id}`}
            className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 transition hover:shadow-lg">
            <p className="text-xs font-semibold text-brand">{j.company_name}</p>
            <h3 className="font-semibold text-navy">{j.title}</h3>
            <p className="mt-1 text-xs text-slate-500">Min CGPA {j.min_cgpa} | CTC {j.ctc_lpa} LPA | {j.shortlisted} shortlisted</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {j.required_skills.map((s) => (
                <span key={s} className="rounded-md bg-slate-100 px-2 py-0.5 text-xs">{s}</span>
              ))}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}