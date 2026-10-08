import { useEffect, useState } from "react";
import api from "../../api";

const STATUS = ["issued", "accepted", "deferred", "withdrawn", "joined"];
const DOCS = ["pending", "submitted", "verified"];
const tone = {
  issued: "bg-blue-50",
  accepted: "bg-emerald-50",
  joined: "bg-teal-50",
  deferred: "bg-amber-50",
  withdrawn: "bg-rose-50",
};
export default function Offers() {
  const [rows, setRows] = useState([]);
  const load = () => api.get("/offers/").then((r) => setRows(r.data));
  useEffect(() => {
    load();
  }, []);
  const patch = async (id, body) => {
    await api.patch(`/offers/${id}/`, body);
    load();
  };
  const sel = "rounded-lg border border-slate-300 px-2 py-1 text-xs capitalize";
  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold text-navy">
        Offer and Documentation Tracking
      </h1>
      <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs text-slate-500">
            <tr>
              <th className="p-3">Student</th>
              <th>Company / Role</th>
              <th>CTC (LPA)</th>
              <th>Offer status</th>
              <th>Documents</th>
              <th>Bond</th>
              <th>PPO</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((o) => (
              <tr key={o.id} className="border-t">
                <td className="p-3">
                  <p className="font-medium">{o.student_name}</p>
                  <p className="text-xs text-slate-500">{o.roll_no}</p>
                </td>
                <td>
                  {o.company} - {o.job_title}
                </td>
                <td>{o.ctc_lpa}</td>
                <td>
                  <select
                    value={o.status}
                    onChange={(e) => patch(o.id, { status: e.target.value })}
                    className={`${sel} ${tone[o.status]}`}
                  >
                    {STATUS.map((s) => (
                      <option key={s}>{s}</option>
                    ))}
                  </select>
                </td>
                <td>
                  <select
                    value={o.docs_status}
                    onChange={(e) =>
                      patch(o.id, { docs_status: e.target.value })
                    }
                    className={sel}
                  >
                    {DOCS.map((s) => (
                      <option key={s}>{s}</option>
                    ))}
                  </select>
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={o.bond_signed}
                    onChange={(e) =>
                      patch(o.id, { bond_signed: e.target.checked })
                    }
                  />
                </td>
                <td>{o.is_ppo ? "Yes" : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-500">
        Changing a status instantly notifies the student.
      </p>
    </div>
  );
}
