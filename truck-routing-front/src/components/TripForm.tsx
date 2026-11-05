
import { useState } from "react";
import { MapPin, Truck, CalendarClock } from "lucide-react";
import type { TripRequest } from "../types/trip";

interface Props {
  onSubmit: (data: TripRequest) => Promise<void>;
  loading: boolean;
}

export default function TripForm({ onSubmit, loading }: Props) {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [departureTime, setDepartureTime] = useState("");
  const [loadWeight, setLoadWeight] = useState("35000");
  const [interval, setInterval] = useState("25");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    await onSubmit({
      origin: origin.trim(),
      destination: destination.trim(),
      departure_time: new Date(departureTime).toISOString(),
      load_weight_lb: Number(loadWeight),
      checkpoint_interval_miles: Number(interval),
    });
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit}>
      <div className="form-heading">
        <div>
          <span className="eyebrow">NEW JOURNEY</span>
          <h2>Plan your route</h2>
          <p>Find a safer route using forecast weather conditions.</p>
        </div>
        <div className="form-icon">
          <Truck size={23} />
        </div>
      </div>

      <label className="field-label">
        <span><MapPin size={15} /> Starting point</span>
        <input
          value={origin}
          onChange={(e) => setOrigin(e.target.value)}
          placeholder="e.g. New York, NY"
          required
        />
      </label>

      <label className="field-label">
        <span><MapPin size={15} /> Destination</span>
        <input
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          placeholder="e.g. Boston, MA"
          required
        />
      </label>

      <label className="field-label">
        <span><CalendarClock size={15} /> Departure date and time</span>
        <input
          type="datetime-local"
          value={departureTime}
          onChange={(e) => setDepartureTime(e.target.value)}
          required
        />
      </label>

      <label className="field-label">
        <span><Truck size={15} /> Cargo weight (lb)</span>
        <input
          type="number"
          min="0"
          step="1"
          value={loadWeight}
          onChange={(e) => setLoadWeight(e.target.value)}
          required
        />
      </label>

      <label className="field-label">
        <span>Weather checkpoint interval</span>
        <select
          value={interval}
          onChange={(e) => setInterval(e.target.value)}
        >
          <option value="10">Every 10 miles</option>
          <option value="25">Every 25 miles</option>
          <option value="50">Every 50 miles</option>
        </select>
      </label>

      <button className="primary-button" type="submit" disabled={loading}>
        {loading ? "Analyzing routes..." : "Find safest routes"}
      </button>

      <p className="form-footnote">
        Weather conditions are evaluated at estimated arrival times
        along each route.
      </p>
    </form>
  );
}
