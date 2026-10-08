import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../../api";
import MatchCard from "../../components/MatchCard";

const TABS = ["shortlisted", "waitlist", "below_threshold"];

export default function JobMatches() {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [rows, setRows] = useState([]);
  const [fair, setFair] = useState(null);
  const [tab, setTab] = useState("shortlisted");
  const [busy, setBusy] = useState(false);
  const [issued, setIssued] = useState([]);
  const isOfficer = localStorage.getItem("role") === "officer";

  const load = () => {
    api.get(`/jobs/${id}/matches/`).then((r) => setRows(r.data));
    api.get(`/jobs/${id}/fairness/`).then((r) => setFair(r.data));
  };
  useEffect(() => { api.get(`/jobs/${id}/`).then((r) => setJob(r.data)); load(); }, [id]);

  const run = async () => { setBusy(true); await api.post(`/jobs/${id}/match/`); await load(); setBusy(false); };
  const issue = async (m) => {
    await api.post("/offers/", { student: m.student_id, job: Number(id), ctc_lpa: job.ctc_lpa || 0 });
    setIssued([...issued, m.id]);
  };
  const shown = rows.filter((r) => r.status === tab);

  return (
    <div className="space-y-5">
      {job && (
        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p className="text-xs font-semibold text-brand">{job.company_name}</p>
          <h1 className="text-2xl font-bold text-navy">{job.title}</h1>
          <p className="mt-2 text-sm text-slate-600">{job.description}</p>
          <p className="mt-3 text-xs font-semibold text-slate-500">AI-extracted requirements</p>
          <div className="mt-1 flex flex-wrap items-center gap-1.5">
            {job.required_skills.map((s) => (
              <span key={s} className="rounded-md bg-brand/10 px-2 py-0.5 text-xs font-medium text-teal-700">{s}</span>
            ))}
            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs">CGPA {job.min_cgpa}+</span>
            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs">Max backlogs {job.max_backlogs}</span>
            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs">
              Branches: {job.allowed_branches.length ? job.allowed_branches.join(", ") : "All"}
            </span>
          </div>
        </div>
      )}

      {fair && fair.rates.length > 0 && (
        <div className={`rounded-2xl p-5 ring-1 ${fair.flag ? "bg-rose-50 ring-rose-200" : "bg-white ring-slate-200"}`}>
          <p className="font-semibold text-navy">Fairness check: shortlisting rate by branch</p>
          <div className="mt-2 flex flex-wrap gap-4 text-sm">
            {fair.rates.map((r) => <span key={r.branch}><b>{r.branch}</b> {r.rate}%</span>)}
          </div>
          <p className="mt-2 text-xs text-slate-600">
            Parity ratio {fair.ratio}.{" "}
            {fair.flag ? "Below 0.8: review the criteria for possible bias." : "Within the 0.8 guideline."}
          </p>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {TABS.map((t) => (
            <button key={t} onClick={() => setTab(t)}
              className={`rounded-full px-4 py-1.5 text-sm ${tab === t ? "bg-navy text-white" : "bg-white ring-1 ring-slate-200"}`}>
              {t.replace("_", " ")} ({rows.filter((r) => r.status === t).length})
            </button>
          ))}
        </div>
        <button onClick={run} disabled={busy}
          className="rounded-xl bg-brand px-5 py-2.5 font-semibold text-white shadow hover:opacity-90 disabled:opacity-60">
          {busy ? "Analysing profiles..." : "Run AI Matching"}
        </button>
      </div>

      {rows.length === 0 && <p className="text-slate-500">No matches yet. Click "Run AI Matching".</p>}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {shown.map((m) => (
          <MatchCard key={m.id} m={m}>
            {isOfficer && m.status === "shortlisted" && (
              <button disabled={issued.includes(m.id)} onClick={() => issue(m)}
                className="mt-3 w-full rounded-xl bg-navy py-2 text-sm font-semibold text-white disabled:bg-emerald-600">
                {issued.includes(m.id) ? "Offer issued" : "Issue offer"}
              </button>
            )}
          </MatchCard>
        ))}
      </div>
    </div>
  );
}