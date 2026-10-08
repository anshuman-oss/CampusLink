import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import api from "../../api";

const empty = {
  job: "",
  venue: "",
  panel: "",
  date: "",
  start_time: "",
  end_time: "",
};
export default function Drives() {
  const [drives, setDrives] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [f, setF] = useState(empty);
  const [result, setResult] = useState(null);
  const load = () => api.get("/drives/").then((r) => setDrives(r.data));
  useEffect(() => {
    load();
    api.get("/jobs/").then((r) => setJobs(r.data));
  }, []);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const submit = async (e, data = f) => {
    e?.preventDefault();
    try {
      await api.post("/drives/", data);
      setResult({ ok: true });
      setF(empty);
      load();
    } catch (x) {
      if (x.response?.status === 409)
        setResult({ ok: false, ...x.response.data });
      else setResult({ ok: false, error: JSON.stringify(x.response?.data) });
    }
  };
  const useSlot = () => {
    const s = result.suggested_slot;
    const data = {
      ...f,
      date: s.date,
      start_time: s.start_time,
      end_time: s.end_time,
    };
    setF(data);
    submit(null, data);
  };
  const input = "rounded-xl border border-slate-300 px-3 py-2.5 text-sm";
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Drive Scheduling</h1>
      <form
        onSubmit={submit}
        className="grid gap-3 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 md:grid-cols-3"
      >
        <select required value={f.job} onChange={set("job")} className={input}>
          <option value="">Select company / job</option>
          {jobs.map((j) => (
            <option key={j.id} value={j.id}>
              {j.company_name} - {j.title}
            </option>
          ))}
        </select>
        <input
          required
          placeholder="Venue (e.g. Main Auditorium)"
          value={f.venue}
          onChange={set("venue")}
          className={input}
        />
        <input
          required
          placeholder="Interview panel (e.g. Panel A)"
          value={f.panel}
          onChange={set("panel")}
          className={input}
        />
        <input
          required
          type="date"
          value={f.date}
          onChange={set("date")}
          className={input}
        />
        <input
          required
          type="time"
          value={f.start_time}
          onChange={set("start_time")}
          className={input}
        />
        <input
          required
          type="time"
          value={f.end_time}
          onChange={set("end_time")}
          className={input}
        />
        <button className="rounded-xl bg-brand py-2.5 font-semibold text-white md:col-span-3">
          Check conflicts and schedule
        </button>
      </form>
      {result && !result.ok && result.conflicts && (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-5">
          <p className="flex items-center gap-2 font-semibold text-rose-700">
            <AlertTriangle size={18} /> Scheduling conflict detected
          </p>
          <ul className="mt-2 space-y-1 text-sm text-rose-800">
            {result.conflicts.map((c, i) => (
              <li key={i}>
                {c.type === "VENUE" && `Venue already booked by ${c.with}`}
                {c.type === "PANEL" &&
                  `Interview panel already assigned to ${c.with}`}
                {c.type === "STUDENT" &&
                  `${c.count} shortlisted students also have a drive with ${c.with}`}
              </li>
            ))}
          </ul>
          {result.suggested_slot && (
            <button
              onClick={useSlot}
              className="mt-3 rounded-xl bg-navy px-4 py-2 text-sm font-semibold text-white"
            >
              Use suggested slot: {result.suggested_slot.date}{" "}
              {result.suggested_slot.start_time}-
              {result.suggested_slot.end_time}
            </button>
          )}
        </div>
      )}
      {result?.error && <p className="text-sm text-rose-600">{result.error}</p>}
      {result?.ok && (
        <p className="flex items-center gap-2 rounded-xl bg-emerald-50 p-4 text-sm font-medium text-emerald-700">
          <CheckCircle2 size={18} /> Drive scheduled. Shortlisted students have
          been notified.
        </p>
      )}
      <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs text-slate-500">
            <tr>
              <th className="p-3">Company / Job</th>
              <th>Date</th>
              <th>Time</th>
              <th>Venue</th>
              <th>Panel</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {drives.map((d) => (
              <tr key={d.id} className="border-t">
                <td className="p-3 font-medium">
                  {d.company} - {d.job_title}
                </td>
                <td>{d.date}</td>
                <td>
                  {d.start_time.slice(0, 5)}-{d.end_time.slice(0, 5)}
                </td>
                <td>{d.venue}</td>
                <td>{d.panel}</td>
                <td className="capitalize">{d.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
