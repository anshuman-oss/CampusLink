import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import { HOME, getRole } from "./auth";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import StudentDashboard from "./pages/student/Dashboard";
import Jobs from "./pages/recruiter/Jobs";
import JobMatches from "./pages/recruiter/JobMatches";
import OfficerDashboard from "./pages/officer/Dashboard";
import Students from "./pages/officer/Students";
import Accounts from "./pages/officer/Accounts";
import Drives from "./pages/officer/Drives";
import Offers from "./pages/officer/Offers";
import AtRisk from "./pages/officer/AtRisk";

function Guard({ roles, children }) {
  const role = getRole();
  if (!role || !localStorage.getItem("access")) return <Navigate to="/" replace />;
  if (roles && !roles.includes(role)) return <Navigate to={HOME[role]} replace />;
  return <Layout>{children}</Layout>;
}

const G = (roles, el) => <Guard roles={roles}>{el}</Guard>;

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/profile" element={G(null, <Profile />)} />
      <Route path="/student" element={G(["student"], <StudentDashboard />)} />
      <Route path="/recruiter" element={G(["recruiter", "officer"], <Jobs />)} />
      <Route path="/recruiter/jobs/:id" element={G(["recruiter", "officer"], <JobMatches />)} />
      <Route path="/officer" element={G(["officer", "mentor"], <OfficerDashboard />)} />
      <Route path="/officer/students" element={G(["officer"], <Students />)} />
      <Route path="/officer/accounts" element={G(["officer"], <Accounts />)} />
      <Route path="/officer/drives" element={G(["officer"], <Drives />)} />
      <Route path="/officer/offers" element={G(["officer"], <Offers />)} />
      <Route path="/officer/at-risk" element={G(["officer", "mentor"], <AtRisk />)} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}