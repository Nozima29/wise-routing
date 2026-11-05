
import { Clock3, RefreshCw } from "lucide-react";

interface Props {
  value: number;
  onChange: (value: number) => void;
  onApply: () => void;
  loading: boolean;
  forecastTime?: string;
}

export default function HeatmapControls({
  value,
  onChange,
  onApply,
  loading,
  forecastTime,
}: Props) {
  return (
    <div className="heatmap-controls">
      <div className="heatmap-controls-heading">
        <div>
          <span className="eyebrow">WEATHER FORECAST</span>
          <h3>Forecast timeline</h3>
        </div>

        <span className="forecast-hour">
          +{value} hours
        </span>
      </div>

      <input
        className="forecast-slider"
        type="range"
        min="0"
        max="48"
        step="1"
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />

      <div className="slider-labels">
        <span>Departure · 0h</span>
        <span>12h</span>
        <span>24h</span>
        <span>36h</span>
        <span>48h</span>
      </div>

      <div className="forecast-footer">
        <div>
          <span className="stat-label">Selected forecast time</span>
          <strong>
            {forecastTime
              ? new Date(forecastTime).toLocaleString()
              : "Not loaded yet"}
          </strong>
        </div>

        <button
          type="button"
          className="refresh-button"
          onClick={onApply}
          disabled={loading}
        >
          <RefreshCw size={15} />
          {loading ? "Loading..." : "Update map"}
        </button>
      </div>
    </div>
  );
}
