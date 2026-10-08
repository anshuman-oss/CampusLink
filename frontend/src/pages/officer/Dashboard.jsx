import { useEffect, useState } from "react";
import { Users, GraduationCap, BadgeCheck, Briefcase, CalendarClock, IndianRupee } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import api from "../../api";
import StatCard from "../../components/StatCard";

const COLORS = ["#14B8A6", "#F59E0B", "#0B1F3A", "#EF4444", "#8B5CF6"];

function Panel({ title, children }) {
  
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <h3 className="mb-3 font-semibold text-navy">{title}</h3>
      {children}
    </div>
  );
}
export default function OfficerDashboard() {
  const [s, setS] = useState(null);
  useEffect(() => { api.get("/analytics/summary/").then((r) => setS(r.data)); }, []);
  if (!s) return <p>Loading dashboard...</p>;
  const f1 = (x) => (x || 0).toFixed(1);
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Placement Command Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
        <StatCard icon={Users} label="Students registered" value={s.total} />
        <StatCard icon={GraduationCap} label="Placement-ready" value={s.ready} tone="bg-emerald-100 text-emerald-700" />
        <StatCard icon={BadgeCheck} label="Placed" value={s.placed} tone="bg-amber-100 text-amber-700" />
        <StatCard icon={Briefcase} label="Active jobs" value={s.active_jobs} />
        <StatCard icon={CalendarClock} label="Upcoming drives" value={s.upcoming_drives} tone="bg-violet-100 text-violet-700" />
        <StatCard icon={IndianRupee} label="Avg / highest LPA" value={`${f1(s.offers.avg)} / ${f1(s.offers.top)}`} tone="bg-rose-100 text-rose-700" />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Branch-wise placement conversion (%)">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={s.branch_conversion}><CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="branch" /><YAxis /><Tooltip /><Bar dataKey="rate" fill="#14B8A6" radius={[6, 6, 0, 0]} /></BarChart>
          </ResponsiveContainer>
        </Panel>
        <Panel title="Skill-wise placement conversion (%)">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={s.skill_conversion} layout="vertical"><XAxis type="number" /><YAxis type="category" dataKey="skill" width={110} />
              <Tooltip /><Bar dataKey="rate" fill="#F59E0B" radius={[0, 6, 6, 0]} /></BarChart>
          </ResponsiveContainer>
        </Panel>
        <Panel title="Offer status">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart><Pie data={s.offer_status} dataKey="n" nameKey="status" outerRadius={90} label>
              {s.offer_status.map((_, i) => <Cell key={i} fill={COLORS[i % 5]} />)}</Pie><Tooltip /><Legend /></PieChart>
          </ResponsiveContainer>
        </Panel>
        <Panel title="Average package by recruiter (LPA)">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={s.package_by_company}><XAxis dataKey="company" /><YAxis /><Tooltip />
              <Bar dataKey="avg" fill="#0B1F3A" radius={[6, 6, 0, 0]} /></BarChart>
          </ResponsiveContainer>
        </Panel>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Documentation status">
          <div className="flex gap-3">
            {s.docs_status.map((d) => (
              <div key={d.docs_status} className="flex-1 rounded-xl bg-slate-50 p-4 text-center">
                <p className="text-2xl font-bold text-navy">{d.n}</p>
                <p className="text-xs capitalize text-slate-500">{d.docs_status}</p>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Recruiter pipeline and engagement">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs text-slate-500"><th>Recruiter</th><th>Jobs</th><th>Offers</th></tr></thead>
            <tbody>{s.pipeline.map((p) => (
              <tr key={p.name} className="border-t"><td className="py-2 font-medium">{p.name}</td><td>{p.jobs_n}</td><td>{p.offers_n}</td></tr>
            ))}</tbody>
          </table>
        </Panel>
      </div>
    </div>
  );
}