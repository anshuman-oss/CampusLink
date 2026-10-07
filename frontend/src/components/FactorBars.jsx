export default function FactorBars({ data, max = 40 }) {
  return (
    <div className="space-y-1.5">
      {Object.entries(data || {}).map(([k, v]) => (
        <div key={k} className="flex items-center gap-2 text-xs text-slate-600">
          <span className="w-36 shrink-0">{k}</span>
          <div className="h-2 flex-1 rounded-full bg-slate-100">
            <div className="h-2 rounded-full bg-brand transition-all duration-700"
              style={{ width: `${Math.min((v / max) * 100, 100)}%` }} />
          </div>
          <span className="w-8 text-right font-medium">{v}</span>
        </div>
      ))}
    </div>
  );
}