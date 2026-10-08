import { useEffect, useState } from "react";
import api from "../../api";

export default function AtRisk() {
  const [rows, setRows] = useState(null);
  useEffect(() => { api.get("/analytics/at-risk/").then((r) => setRows(r.data)); }, []);
  if (!rows) return <p>Running prediction model...</p>;
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-navy">Students at Risk of Remaining Unplaced</h1>
        <p className="text-sm text-slate-500">Predicted by a logistic regression model trained on the previous batch. {rows.length} students flagged.</p>
      </div>
      <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs text-slate-500">
            <tr><th className="p-3">Student</th><th>Branch</th><th>Placement probability</th><th>Weak areas</th><th>Mentor</th></tr>
          </thead>
          <tbody>{rows.map((r) => (
            <tr key={r.id} className="border-t">
              <td className="p-3"><p className="font-medium">{r.name}</p><p className="text-xs text-slate-500">{r.roll_no}</p></td>
              <td>{r.branch}</td>
              <td className="w-56">
                <div className="flex items-center gap-2">
                  <div className="h-2 flex-1 rounded-full bg-slate-100">
                    <div className="h-2 rounded-full bg-rose-500" style={{ width: `${r.probability}%` }} />
                  </div>
                  <span className="text-xs font-semibold">{r.probability}%</span>
                </div>
              </td>
              <td><div className="flex flex-wrap gap-1">{r.weak_areas.map((w) => (
                <span key={w} className="rounded-md bg-rose-50 px-2 py-0.5 text-xs text-rose-700">{w}</span>))}</div></td>
              <td className="text-xs">{r.mentor || "-"}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </div>
  );
}