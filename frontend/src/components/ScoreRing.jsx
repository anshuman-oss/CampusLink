export default function ScoreRing({ value, size = 72 }) {
  const r = 30, c = 2 * Math.PI * r, off = c - (Math.min(value, 100) / 100) * c;
  const color = value >= 80 ? "#16A34A" : value >= 60 ? "#14B8A6" : value >= 40 ? "#F59E0B" : "#EF4444";
  return (
    <svg width={size} height={size} viewBox="0 0 72 72" className="shrink-0">
      <circle cx="36" cy="36" r={r} stroke="#E2E8F0" strokeWidth="7" fill="none" />
      <circle cx="36" cy="36" r={r} stroke={color} strokeWidth="7" fill="none" strokeLinecap="round"
        strokeDasharray={c} strokeDashoffset={off} transform="rotate(-90 36 36)"
        style={{ transition: "stroke-dashoffset .8s ease" }} />
      <text x="36" y="41" textAnchor="middle" fontSize="16" fontWeight="700" fill="#0B1F3A">
        {Math.round(value)}
      </text>
    </svg>
  );
}