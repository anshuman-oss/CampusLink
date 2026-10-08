import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";
import { errText } from "../auth";

const input = "w-full rounded-xl border border-slate-300 px-4 py-2.5 outline-none focus:border-brand focus:ring-2 focus:ring-brand/30";

export default function Register() {
  const [role, setRole] = useState("student");
  const [f, setF] = useState({
    roll_no: "", email: "", password: "", confirm: "", username: "",
    first_name: "", last_name: "", phone: "", company_name: "",
  });
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    if (f.password !== f.confirm) { setErr("Passwords do not match."); return; }
    setBusy(true);
    try {
      const { confirm, ...body } = f;
      const { data } = await api.post("/auth/register/", { ...body, role });
      setOk(data.detail);
      if (role === "student") setTimeout(() => navigate("/"), 1800);
    } catch (x) { setErr(errText(x)); }
    setBusy(false);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <form onSubmit={submit} className="w-full max-w-lg space-y-4 rounded-2xl bg-white p-8 shadow-lg ring-1 ring-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-navy">Create your CampusLink account</h1>
          <p className="text-sm text-slate-500">Placement officers and mentors are created by the placement cell.</p>
        </div>

        <div className="grid grid-cols-2 gap-2 rounded-xl bg-slate-100 p-1">
          {[["student", "I am a student"], ["recruiter", "I am a recruiter"]].map(([r, label]) => (
            <button type="button" key={r} onClick={() => { setRole(r); setErr(""); setOk(""); }}
              className={`rounded-lg py-2 text-sm font-medium ${role === r ? "bg-white text-navy shadow" : "text-slate-500"}`}>
              {label}
            </button>
          ))}
        </div>

        {role === "student" ? (
          <>
            <p className="rounded-lg bg-teal-50 p-3 text-xs text-teal-800">
              Your placement cell must have added you to the college roster first. Use the roll number and
              email that the cell registered. Your roll number will be your username.
            </p>
            <input required placeholder="Roll number" value={f.roll_no} onChange={set("roll_no")} className={input} />
            <input required type="email" placeholder="College email (as on the roster)" value={f.email} onChange={set("email")} className={input} />
          </>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-3">
              <input required placeholder="First name" value={f.first_name} onChange={set("first_name")} className={input} />
              <input placeholder="Last name" value={f.last_name} onChange={set("last_name")} className={input} />
            </div>
            <input required placeholder="Company name" value={f.company_name} onChange={set("company_name")} className={input} />
            <input required type="email" placeholder="Work email" value={f.email} onChange={set("email")} className={input} />
            <div className="grid grid-cols-2 gap-3">
              <input required placeholder="Choose a username" value={f.username} onChange={set("username")} className={input} />
              <input placeholder="Phone (optional)" value={f.phone} onChange={set("phone")} className={input} />
            </div>
            <p className="rounded-lg bg-amber-50 p-3 text-xs text-amber-800">
              A placement officer will review and approve your account before you can log in.
            </p>
          </>
        )}

        <div className="grid grid-cols-2 gap-3">
          <input required type="password" placeholder="Password" value={f.password} onChange={set("password")} className={input} />
          <input required type="password" placeholder="Confirm password" value={f.confirm} onChange={set("confirm")} className={input} />
        </div>
        <p className="text-xs text-slate-500">At least 8 characters, not too common, and not entirely numeric.</p>

        {err && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{err}</p>}
        {ok && <p className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-700">{ok}</p>}

        <button disabled={busy} className="w-full rounded-xl bg-brand py-3 font-semibold text-white shadow hover:opacity-90 disabled:opacity-60">
          {busy ? "Please wait..." : role === "student" ? "Activate account" : "Register"}
        </button>
        <p className="text-center text-sm text-slate-600">
          Already have an account? <Link to="/" className="font-semibold text-brand">Sign in</Link>
        </p>
      </form>
    </div>
  );
}