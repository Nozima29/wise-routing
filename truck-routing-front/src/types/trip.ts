
export type RiskLevel =
  | "low"
  | "moderate"
  | "high"
  | "severe"
  | "no_travel";

export interface TripRequest {
  origin: string;
  destination: string;
  departure_time: string;
  load_weight_lb: number;
  checkpoint_interval_miles: number;
}

export interface Checkpoint {
  id: number;
  sequence: number;
  distance_from_origin_miles: number;
  latitude: number;
  longitude: number;
  estimated_arrival: string;
  temperature_f: number | null;
  wind_speed_mph: number | null;
  precipitation_in_per_hour: number | null;
  snowfall_in_per_hour: number | null;
  visibility_miles: number | null;
  risk_level: RiskLevel;
  risk_score: number;
  risk_reason: string;
}

export interface Route {
  id: number;
  alternative_number: number;
  provider: string;
  geometry: {
    type: "LineString";
    coordinates: [number, number][];
  };
  distance_miles: number;
  duration_seconds: number;
  severe_miles: number;
  high_miles: number;
  average_risk: number;
  overall_risk: RiskLevel;
  is_recommended: boolean;
  is_no_travel: boolean;
  checkpoints: Checkpoint[];
}

export interface Trip {
  id: number;
  origin: string;
  destination: string;
  departure_time: string;
  load_weight_lb: number;
  checkpoint_interval_miles: number;
  status: "pending" | "processing" | "completed" | "failed";
  routes: Route[];
}

export interface HeatmapPoint {
  sequence: number;
  distance_from_origin_miles: number;
  latitude: number;
  longitude: number;
  temperature_f: number | null;
  wind_speed_mph: number | null;
  precipitation_in_per_hour: number | null;
  snowfall_in_per_hour: number | null;
  visibility_miles: number | null;
  risk_level: RiskLevel;
  risk_score: number;
  risk_reason: string;
}

export interface HeatmapResponse {
  trip_id: number;
  route_id: number;
  offset_hours: number;
  forecast_time: string;
  interval_miles: number;
  points: HeatmapPoint[];
}
