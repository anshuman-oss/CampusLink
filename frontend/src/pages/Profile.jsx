import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import { errText, logout } from "../auth";

const input = "w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/30";
const ROLE_TONE = {
  student: "bg-emerald-100 text-emerald-700", recruiter: "bg-violet-100 text-violet-700",
  officer: "bg-amber-100 text-amber-700", mentor: "bg-sky-100 text-sky-700",
};

function Card({ title, children }) {
  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h2 className="mb-4 font-semibold text-navy">{title}</h2>
      {children}
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between border-b border-slate-100 py-2 text-sm last:border-0">
      <span className="text-slate-500">{label}</span>
      <span className="font-medium text-slate-800">{value ?? "-"}</span>
    </div>
  );
}

export default function Profile() {
  const [me, setMe] = useState(null);
  const [f, setF] = useState({});
  const [msg, setMsg] = useState({});
  const [pw, setPw] = useState({ old_password: "", new_password: "", confirm: "" });
  const navigate = useNavigate();

  const fill = (d) => setF({
    first_name: d.first_name, last_name: d.last_name, email: d.email, phone: d.phone,
    company_name: d.company?.name || "", industry: d.company?.industry || "",
  });
  useEffect(() => { api.get("/auth/me/").then((r) => { setMe(r.data); fill(r.data); }); }, []);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    try {
      const body = { first_name: f.first_name, last_name: f.last_name, email: f.email, phone: f.phone };
      if (me.role === "recruiter") { body.company_name = f.company_name; body.industry = f.industry; }
      const { data } = await api.patch("/auth/me/", body);
      setMe(data); fill(data);
      localStorage.setItem("name", data.name);
      setMsg({ profile: { ok: true, t: "Profile updated." } });
    } catch (x) { setMsg({ profile: { ok: false, t: errText(x) } }); }
  };

  const changePw = async (e) => {
    e.preventDefault();
    if (pw.new_password !== pw.confirm) { setMsg({ pw: { ok: false, t: "New passwords do not match." } }); return; }
    try {
      await api.post("/auth/change-password/", { old_password: pw.old_password, new_password: pw.new_password });
      await logout();
      navigate("/");
    } catch (x) { setMsg({ pw: { ok: false, t: errText(x) } }); }
  };

  if (!me) return <p>Loading profile...</p>;
  const Msg = ({ m }) => m && <p className={`rounded-lg p-3 text-sm ${m.ok ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>{m.t}</p>;
  const initials = me.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  const date = (d) => (d ? new Date(d).toLocaleString() : "-");

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-5 rounded-2xl bg-gradient-to-r from-navy to-[#12305a] p-6 text-white">
        <span className="flex h-20 w-20 items-center justify-center rounded-full bg-brand text-2xl font-bold">{initials}</span>
        <div>
          <h1 className="text-2xl font-bold">{me.name}</h1>
          <p className="text-sm text-slate-300">@{me.username}</p>
          <span className={`mt-2 inline-block rounded-full px-3 py-0.5 text-xs font-semibold ${ROLE_TONE[me.role]}`}>{me.role_label}</span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Account details">
          <Row label="Role" value={me.role_label} />
          <Row label="Username" value={me.username} />
          <Row label="Email" value={me.email} />
          <Row label="Phone" value={me.phone || "-"} />
          <Row label="Member since" value={date(me.date_joined)} />
          <Row label="Last login" value={date(me.last_login)} />
          {me.role === "student" && me.student && (<>
            <Row label="Roll number" value={me.student.roll_no} />
            <Row label="Branch" value={me.student.branch} />
            <Row label="CGPA" value={me.student.cgpa} />
            <Row label="Backlogs" value={me.student.backlogs} />
            <Row label="Readiness" value={`${me.student.readiness_score} (${me.student.readiness_level})`} />
            <Row label="Mentor" value={me.student.mentor || "Not assigned yet"} />
            <Row label="Placement status" value={me.student.placed ? "Placed" : "Not placed yet"} />
          </>)}
          {me.role === "recruiter" && me.company && (<>
            <Row label="Company" value={me.company.name} />
            <Row label="Industry" value={me.company.industry || "-"} />
            <Row label="Jobs posted" value={me.company.jobs} />
            <Row label="Account status" value={me.approved ? "Approved" : "Pending approval"} />
          </>)}
          {me.role === "mentor" && <Row label="Students mentored" value={me.mentees} />}
        </Card>

        <Card title="Edit profile">
          <form onSubmit={save} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <input value={f.first_name || ""} onChange={set("first_name")} placeholder="First name" className={input} />
              <input value={f.last_name || ""} onChange={set("last_name")} placeholder="Last name" className={input} />
            </div>
            <input type="email" value={f.email || ""} onChange={set("email")} placeholder="Email" className={input} />
            <input value={f.phone || ""} onChange={set("phone")} placeholder="Phone" className={input} />
            {me.role === "recruiter" && (<>
              <input value={f.company_name} onChange={set("company_name")} placeholder="Company name" className={input} />
              <input value={f.industry} onChange={set("industry")} placeholder="Industry" className={input} />
            </>)}
            <Msg m={msg.profile} />
            <button className="rounded-xl bg-brand px-5 py-2.5 text-sm font-semibold text-white hover:opacity-90">Save changes</button>
            {me.role === "student" && (
              <p className="text-xs text-slate-500">CGPA, branch and assessment scores are set by the placement cell.</p>
            )}
          </form>
        </Card>
      </div>

      <Card title="Change password">
        <form onSubmit={changePw} className="grid gap-3 md:grid-cols-4">
          <input required type="password" placeholder="Current password" value={pw.old_password}
            onChange={(e) => setPw({ ...pw, old_password: e.target.value })} className={input} />
          <input required type="password" placeholder="New password" value={pw.new_password}
            onChange={(e) => setPw({ ...pw, new_password: e.target.value })} className={input} />
          <input required type="password" placeholder="Confirm new password" value={pw.confirm}
            onChange={(e) => setPw({ ...pw, confirm: e.target.value })} className={input} />
          <button className="rounded-xl bg-navy px-5 py-2.5 text-sm font-semibold text-white hover:opacity-90">Update password</button>
          <div className="md:col-span-4"><Msg m={msg.pw} /></div>
        </form>
        <p className="mt-2 text-xs text-slate-500">You will be signed out after changing your password.</p>
      </Card>
    </div>
  );
}