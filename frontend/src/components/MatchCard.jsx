import ScoreRing from "./ScoreRing";
import FactorBars from "./FactorBars";

const badge = {
  shortlisted: "bg-emerald-100 text-emerald-700",
  waitlist: "bg-amber-100 text-amber-700",
  below_threshold: "bg-rose-100 text-rose-700",
};
export default function MatchCard({ m }) {
  const ex = m.explanation || {};
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 transition hover:shadow-lg">
      <div className="flex items-center gap-4">
        <ScoreRing value={m.fit_score} />
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-semibold text-navy">{m.name || m.candidate_id}</h3>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${badge[m.status]}`}>
              {m.status.replace("_", " ")}
            </span>
            {ex.hidden_gem && (
              <span className="rounded-full bg-gold/20 px-2 py-0.5 text-xs font-medium text-amber-700">Hidden Gem</span>
            )}
          </div>
          <p className="text-xs text-slate-500">
            {m.roll_no ? `${m.roll_no} | ` : ""}{m.branch} | CGPA {m.cgpa} | {m.level}
          </p>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {(ex.matched || []).map((s) => (
          <span key={s} className="rounded-md bg-emerald-50 px-2 py-0.5 text-xs text-emerald-700">{s}</span>
        ))}
        {(ex.missing || []).map((s) => (
          <span key={s} className="rounded-md bg-rose-50 px-2 py-0.5 text-xs text-rose-700">gap: {s}</span>
        ))}
      </div>
      <div className="mt-3"><FactorBars data={ex.factors} /></div>
      <p className="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{ex.summary}</p>
      {ex.suggestions?.length > 0 && (
        <p className="mt-2 text-xs text-slate-500"><b>Next step:</b> {ex.suggestions[0]}</p>
      )}
    </div>
  );
}