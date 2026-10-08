import { useEffect, useState } from "react";
import { Pencil, Plus, Search, Trash2, Upload } from "lucide-react";
import api from "../../api";
import { errText } from "../../auth";

const BRANCHES = ["CSE", "IT", "ECE", "EEE", "ME", "CE"];
const input = "w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/30";
const EMPTY = { roll_no: "", first_name: "", last_name: "", email: "", branch: "CSE", cgpa: "", backlogs: 0,
                batch: 2026, aptitude_score: 0, mock_score: 0, soft_score: 0, mentor: "" };
const LEVEL = { "Not Ready": "bg-rose-100 text-rose-700", Developing: "bg-amber-100 text-amber-700",
                Ready: "bg-teal-100 text-teal-700", "Highly Employable": "bg-emerald-100 text-emerald-700" };

function Field({ label, children }) {
  return <label className="block text-xs font-medium text-slate-600">{label}<div className="mt-1">{children}</div></label>;
}

function StudentForm({ initial, mentors, onClose, onSaved }) {
  const editing = !!initial.id;
  const [f, setF] = useState({ ...EMPTY, ...initial, mentor: initial.mentor ?? "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    const body = { ...f, mentor: f.mentor === "" ? null : Number(f.mentor) };
    if (body.cgpa === "") delete body.cgpa;
    try {
      if (editing) await api.patch(`/students/roster/${initial.id}/`, body);
      else await api.post("/students/roster/", body);
      onSaved();
    } catch (x) { setErr(errText(x)); }
    setBusy(false);
  };

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 p-4">
      <form onSubmit={submit} className="max-h-[92vh] w-full max-w-2xl space-y-4 overflow-auto rounded-2xl bg-white p-6 shadow-2xl">
        <h2 className="text-lg font-bold text-navy">{editing ? "Edit student" : "Add student to roster"}</h2>
        <div className="grid gap-3 md:grid-cols-2">
          <Field label="Roll number (this is the login username)">
            <input required disabled={editing} value={f.roll_no} onChange={set("roll_no")} className={`${input} disabled:bg-slate-100`} />
          </Field>
          <Field label="Email (student must use this to activate)">
            <input required type="email" value={f.email} onChange={set("email")} className={input} />
          </Field>
          <Field label="First name"><input required value={f.first_name} onChange={set("first_name")} className={input} /></Field>
          <Field label="Last name"><input value={f.last_name} onChange={set("last_name")} className={input} /></Field>
          <Field label="Branch">
            <select value={f.branch} onChange={set("branch")} className={input}>{BRANCHES.map((b) => <option key={b}>{b}</option>)}</select>
          </Field>
          <Field label="Batch (passing-out year)"><input type="number" value={f.batch} onChange={set("batch")} className={input} /></Field>
          <Field label="CGPA (0 to 10)"><input type="number" step="0.01" min="0" max="10" value={f.cgpa} onChange={set("cgpa")} className={input} /></Field>
          <Field label="Active backlogs"><input type="number" min="0" value={f.backlogs} onChange={set("backlogs")} className={input} /></Field>
        </div>
        <p className="border-t border-slate-200 pt-3 text-xs font-semibold text-slate-500">Assessment scores (0 to 100)</p>
        <div className="grid gap-3 md:grid-cols-3">
          <Field label="Aptitude"><input type="number" min="0" max="100" value={f.aptitude_score} onChange={set("aptitude_score")} className={input} /></Field>
          <Field label="Mock interview"><input type="number" min="0" max="100" value={f.mock_score} onChange={set("mock_score")} className={input} /></Field>
          <Field label="Soft skills"><input type="number" min="0" max="100" value={f.soft_score} onChange={set("soft_score")} className={input} /></Field>
        </div>
        <Field label="Mentor">
          <select value={f.mentor} onChange={set("mentor")} className={input}>
            <option value="">No mentor</option>
            {mentors.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
          </select>
        </Field>
        {err && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{err}</p>}
        <div className="flex justify-end gap-3">
          <button type="button" onClick={onClose} className="rounded-xl px-5 py-2.5 text-sm text-slate-600 hover:bg-slate-100">Cancel</button>
          <button disabled={busy} className="rounded-xl bg-brand px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-60">
            {busy ? "Saving..." : "Save"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function Students() {
  const [rows, setRows] = useState([]);
  const [mentors, setMentors] = useState([]);
  const [q, setQ] = useState("");
  const [branch, setBranch] = useState("");
  const [modal, setModal] = useState(null);
  const [report, setReport] = useState(null);

  const load = () => api.get("/students/roster/").then((r) => setRows(r.data));
  useEffect(() => {
    load();
    api.get("/auth/staff/").then((r) => setMentors(r.data.filter((u) => u.role === "mentor")));
  }, []);

  const remove = async (s) => {
    if (!window.confirm(`Remove ${s.first_name} ${s.last_name} (${s.roll_no})? They will no longer be able to log in.`)) return;
    await api.delete(`/students/roster/${s.id}/`);
    load();
  };

  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    try { setReport((await api.post("/students/roster/import/", fd)).data); load(); }
    catch (x) { setReport({ added: 0, errors: [{ row: "-", roll_no: "", error: errText(x) }] }); }
    e.target.value = "";
  };

  const shown = rows.filter((s) =>
    (!branch || s.branch === branch) &&
    `${s.first_name} ${s.last_name} ${s.roll_no} ${s.email}`.toLowerCase().includes(q.toLowerCase()));

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-navy">Student Roster</h1>
          <p className="text-sm text-slate-500">{rows.length} students. Students activate their own account using the roll number and email below.</p>
        </div>
        <div className="flex gap-2">
          <label className="flex cursor-pointer items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-medium text-navy ring-1 ring-slate-300 hover:bg-slate-50">
            <Upload size={16} /> Import CSV
            <input type="file" accept=".csv" onChange={upload} className="hidden" />
          </label>
          <button onClick={() => setModal({})} className="flex items-center gap-2 rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-white shadow">
            <Plus size={16} /> Add student
          </button>
        </div>
      </div>

      {report && (
        <div className="rounded-2xl bg-white p-4 text-sm shadow-sm ring-1 ring-slate-200">
          <p className="font-semibold text-emerald-700">{report.added} student(s) imported.</p>
          {report.errors.length > 0 && (
            <div className="mt-2">
              <p className="font-semibold text-rose-700">{report.errors.length} row(s) skipped:</p>
              <ul className="list-disc pl-5 text-xs text-rose-700">
                {report.errors.map((e, i) => <li key={i}>Row {e.row} {e.roll_no && `(${e.roll_no})`}: {e.error}</li>)}
              </ul>
            </div>
          )}
          <p className="mt-2 text-xs text-slate-500">
            CSV columns: roll_no, first_name, last_name, email, branch, cgpa, backlogs, batch, aptitude_score, mock_score, soft_score
            (roll_no, first_name, email and branch are required).
          </p>
          <button onClick={() => setReport(null)} className="mt-2 text-xs font-semibold text-brand">Dismiss</button>
        </div>
      )}

      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-3 text-slate-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by name, roll number or email" className={`${input} pl-9`} />
        </div>
        <select value={branch} onChange={(e) => setBranch(e.target.value)} className="rounded-xl border border-slate-300 px-3 text-sm">
          <option value="">All branches</option>
          {BRANCHES.map((b) => <option key={b}>{b}</option>)}
        </select>
      </div>

      <div className="overflow-x-auto rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs text-slate-500">
            <tr><th className="p-3">Student</th><th>Branch</th><th>CGPA</th><th>Apt / Mock / Soft</th><th>Readiness</th><th>Mentor</th><th>Account</th><th></th></tr>
          </thead>
          <tbody>
            {shown.map((s) => (
              <tr key={s.id} className="border-t border-slate-100">
                <td className="p-3"><p className="font-medium">{s.first_name} {s.last_name}</p><p className="text-xs text-slate-500">{s.roll_no} | {s.email}</p></td>
                <td>{s.branch}</td><td>{s.cgpa}</td>
                <td>{s.aptitude_score} / {s.mock_score} / {s.soft_score}</td>
                <td><span className={`rounded-full px-2 py-0.5 text-xs font-medium ${LEVEL[s.readiness_level]}`}>{s.readiness_score} {s.readiness_level}</span></td>
                <td className="text-xs">{s.mentor_name || "-"}</td>
                <td className="text-xs">{s.activated ? <span className="text-emerald-700">Activated</span> : <span className="text-amber-700">Awaiting activation</span>}</td>
                <td className="whitespace-nowrap pr-3 text-right">
                  <button onClick={() => setModal(s)} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"><Pencil size={15} /></button>
                  <button onClick={() => remove(s)} className="rounded-lg p-2 text-rose-500 hover:bg-rose-50"><Trash2 size={15} /></button>
                </td>
              </tr>
            ))}
            {shown.length === 0 && <tr><td colSpan="8" className="p-8 text-center text-slate-400">No students yet. Add one or import a CSV file.</td></tr>}
          </tbody>
        </table>
      </div>

      {modal && (
        <StudentForm initial={modal} mentors={mentors} onClose={() => setModal(null)}
          onSaved={() => { setModal(null); load(); }} />
      )}
    </div>
  );
}