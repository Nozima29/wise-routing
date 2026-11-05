
import type { RiskLevel } from "../types/trip";

const levels: {
  level: RiskLevel;
  label: string;
}[] = [
  { level: "low", label: "Low" },
  { level: "moderate", label: "Moderate" },
  { level: "high", label: "High" },
  { level: "severe", label: "Severe" },
  { level: "no_travel", label: "No Travel" },
];

const colors: Record<RiskLevel, string> = {
  low: "#16a36a",
  moderate: "#d6a126",
  high: "#ed862b",
  severe: "#dc4545",
  no_travel: "#782d3b",
};

export default function RiskLegend() {
  return (
    <div className="risk-legend">
      <strong>Weather risk</strong>

      {levels.map(({ level, label }) => (
        <div className="risk-legend-item" key={level}>
          <span
            className="risk-legend-color"
            style={{ backgroundColor: colors[level] }}
          />
          <span>{label}</span>
        </div>
      ))}
    </div>
  );
}
