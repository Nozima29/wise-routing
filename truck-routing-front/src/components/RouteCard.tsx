
import { Clock3, Route as RouteIcon, ShieldCheck, AlertTriangle } from "lucide-react";
import type { Route, RiskLevel } from "../types/trip";

interface Props {
  route: Route;
  selected: boolean;
  onClick: () => void;
}

const riskLabels: Record<RiskLevel, string> = {
  low: "Low",
  moderate: "Moderate",
  high: "High",
  severe: "Severe",
  no_travel: "No Travel",
};

function formatDuration(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  return `${hours}h ${minutes}m`;
}

export default function RouteCard({ route, selected, onClick }: Props) {
  return (
    <button
      type="button"
      className={`route-card ${selected ? "selected" : ""}`}
      onClick={onClick}
    >
      <div className="route-card-top">
        <div>
          <span className="eyebrow">
            ROUTE OPTION {route.alternative_number}
          </span>
          <h3>
            {route.is_recommended ? "Recommended route" : "Alternative route"}
          </h3>
        </div>

        {route.is_recommended ? (
          <span className="recommended-tag">
            <ShieldCheck size={14} /> Best choice
          </span>
        ) : route.is_no_travel ? (
          <span className="unsafe-tag">
            <AlertTriangle size={14} /> No Travel
          </span>
        ) : null}
      </div>

      <div className="route-stats">
        <div>
          <RouteIcon size={16} />
          <strong>{route.distance_miles.toFixed(1)} mi</strong>
          <span>Distance</span>
        </div>
        <div>
          <Clock3 size={16} />
          <strong>{formatDuration(route.duration_seconds)}</strong>
          <span>Travel time</span>
        </div>
      </div>

      <div className="risk-summary">
        <div>
          <span className="stat-label">Overall risk</span>
          <span className={`risk-pill risk-${route.overall_risk}`}>
            {riskLabels[route.overall_risk]}
          </span>
        </div>
        <div>
          <span className="stat-label">Severe miles</span>
          <strong>{route.severe_miles.toFixed(1)} mi</strong>
        </div>
        <div>
          <span className="stat-label">High-risk miles</span>
          <strong>{route.high_miles.toFixed(1)} mi</strong>
        </div>
        <div>
          <span className="stat-label">Average risk</span>
          <strong>{route.average_risk.toFixed(2)} / 5</strong>
        </div>
      </div>

      <span className="view-route">
        {selected ? "Currently selected" : "View route on map"}
      </span>
    </button>
  );
}
