import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, Briefcase, CalendarClock, FileCheck2, AlertTriangle, Bell, LogOut, User } from "lucide-react";
import api from "../api";

const NAV = {
  student: [["/student", "My Readiness", User]],
  recruiter: [["/recruiter", "Jobs & Matches", Briefcase]],
  officer: [["/officer", "Dashboard", LayoutDashboard], ["/recruiter", "Jobs & Matches", Briefcase],
            ["/officer/drives", "Drives", CalendarClock], ["/officer/offers", "Offers", FileCheck2],
            ["/officer/at-risk", "At-Risk Students", AlertTriangle]],
  mentor: [["/officer", "Dashboard", LayoutDashboard], ["/officer/at-risk", "At-Risk Students", AlertTriangle]],
};

export default function Layout({ children }) {
  const role = localStorage.getItem("role");
  const name = localStorage.getItem("name");
  const navigate = useNavigate();
  const [notes, setNotes] = useState([]);
  const [open, setOpen] = useState(false);

  const load = () => api.get("/auth/notifications/").then((r) => setNotes(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);
  const unread = notes.filter((n) => !n.is_read).length;

  const read = async (id) => { await api.post(`/auth/notifications/${id}/read/`); load(); };
  const logout = () => { localStorage.clear(); navigate("/"); };

  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 left-0 flex w-60 flex-col bg-navy text-slate-200">
        <div className="px-6 py-6">
          <h1 className="text-xl font-bold tracking-wide text-white">Campus<span className="text-brand">Link</span></h1>
          <p className="text-[11px] text-slate-400">by Team HireSync</p>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {NAV[role].map(([to, label, Icon]) => (
            <NavLink key={to + label} to={to} end
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
                  isActive ? "bg-brand text-white" : "hover:bg-white/10"}`}>
              <Icon size={18} /> {label}
            </NavLink>
          ))}
        </nav>
        <button onClick={logout} className="m-3 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm hover:bg-white/10">
          <LogOut size={18} /> Logout
        </button>
      </aside>

      <div className="ml-60 flex-1">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b bg-white/80 px-8 py-4 backdrop-blur">
          <div>
            <p className="text-sm font-semibold text-navy">{name}</p>
            <p className="text-xs capitalize text-slate-500">{role === "officer" ? "Placement Officer" : role}</p>
          </div>
          <div className="relative">
            <button onClick={() => setOpen(!open)} className="relative rounded-full bg-slate-100 p-2.5 hover:bg-slate-200">
              <Bell size={18} />
              {unread > 0 && (
                <span className="absolute -right-1 -top-1 rounded-full bg-rose-500 px-1.5 text-[10px] font-bold text-white">{unread}</span>
              )}
            </button>
            {open && (
              <div className="absolute right-0 mt-2 max-h-96 w-80 overflow-auto rounded-2xl bg-white p-2 shadow-xl ring-1 ring-slate-200">
                {notes.length === 0 && <p className="p-4 text-sm text-slate-400">No notifications yet.</p>}
                {notes.map((n) => (
                  <div key={n.id} onClick={() => read(n.id)}
                    className={`cursor-pointer rounded-xl p-3 text-sm hover:bg-slate-50 ${n.is_read ? "opacity-60" : ""}`}>
                    <p className="font-semibold text-navy">{n.title}</p>
                    <p className="text-xs text-slate-600">{n.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </header>
        <main className="p-8">{children}</main>
      </div>
    </div>
  );
}