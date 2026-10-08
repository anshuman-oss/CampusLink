import { useEffect, useState } from "react";
import api from "../../api";
import { errText } from "../../auth";

const input = "w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/30";
const EMPTY = { role: "mentor", username: "", password: "", first_name: "", last_name: "", email: "" };

export default function Accounts() {
  const [pending, setPending] = useState([]);
  const [staff, setStaff] = useState([]);
  const [f, setF] = useState(EMPTY);
  const [msg, setMsg] = useState(null);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const load = () => {
    api.get("/auth/pending/").then((r) => setPending(r.data));
    api.get("/auth/staff/").then((r) => setStaff(r.data));
  };
  useEffect(() => { load(); }, []);

  const decide = async (u, approve) => {
    if (!approve && !window.confirm(`Reject ${u.company || u.username}? They will not be able to log in.`)) return;
    await api.post(`/auth/approve/${u.id}/`, { approve });
    load();
  };

  const create = async (e) => {
    e.preventDefault();
    setMsg(null);
    try {
      await api.post("/auth/staff/", f);
      setMsg({ ok: true, t: `${f.role === "mentor" ? "Mentor" : "Officer"} account created. They can log in now.` });
      setF(EMPTY); load();
    } catch (x) { setMsg({ ok: false, t: errText(x) }); }
  };

  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <div>
          <h1 className="text-2xl font-bold text-navy">Recruiter Approvals</h1>
          <p className="text-sm text-slate-500">Recruiters can log in only after you approve them.</p>
        </div>
        <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs text-slate-500">
              <tr><th className="p-3">Company</th><th>Contact</th><th>Email</th><th>Username</th><th></th></tr>
            </thead>
            <tbody>
              {pending.map((u) => (
                <tr key={u.id} className="border-t border-slate-100">
                  <td className="p-3 font-medium">{u.company}</td><td>{u.name}</td><td>{u.email}</td><td>{u.username}</td>
                  <td className="space-x-2 pr-3 text-right">
                    <button onClick={() => decide(u, true)} className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white">Approve</button>
                    <button onClick={() => decide(u, false)} className="rounded-lg bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700">Reject</button>
                  </td>
                </tr>
              ))}
              {pending.length === 0 && <tr><td colSpan="5" className="p-6 text-center text-slate-400">No recruiters are waiting for approval.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-bold text-navy">Mentors and Officers</h2>
        <form onSubmit={create} className="grid gap-3 rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 md:grid-cols-3">
          <select value={f.role} onChange={set("role")} className={input}>
            <option value="mentor">Mentor</option><option value="officer">Placement Officer</option>
          </select>
          <input required placeholder="Username" value={f.username} onChange={set("username")} className={input} />
          <input required type="password" placeholder="Password" value={f.password} onChange={set("password")} className={input} />
          <input required placeholder="First name" value={f.first_name} onChange={set("first_name")} className={input} />
          <input placeholder="Last name" value={f.last_name} onChange={set("last_name")} className={input} />
          <input required type="email" placeholder="Email" value={f.email} onChange={set("email")} className={input} />
          {msg && <p className={`rounded-lg p-3 text-sm md:col-span-3 ${msg.ok ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>{msg.t}</p>}
          <button className="rounded-xl bg-brand py-2.5 text-sm font-semibold text-white md:col-span-3">Create account</button>
        </form>
        <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs text-slate-500">
              <tr><th className="p-3">Name</th><th>Username</th><th>Email</th><th>Role</th><th>Students mentored</th></tr>
            </thead>
            <tbody>
              {staff.map((u) => (
                <tr key={u.id} className="border-t border-slate-100">
                  <td className="p-3 font-medium">{u.name}</td><td>{u.username}</td><td>{u.email}</td>
                  <td className="capitalize">{u.role}</td><td>{u.role === "mentor" ? u.mentees : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}