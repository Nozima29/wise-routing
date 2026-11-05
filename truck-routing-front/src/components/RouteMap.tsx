
import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import RiskLegend from "./RiskLegend";
import type {
  Route,
  RiskLevel,
  HeatmapPoint,
} from "../types/trip";

interface Props {
  routes: Route[];
  selectedRoute: Route | null;
  heatmapPoints: HeatmapPoint[];
}

const riskColors: Record<RiskLevel, string> = {
  low: "#16a36a",
  moderate: "#d6a126",
  high: "#ed862b",
  severe: "#dc4545",
  no_travel: "#782d3b",
};

function FitRouteBounds({
    positions,
  }: {
    positions: [number, number][];
  }) {
    const map = useMap();

    useEffect(() => {
      if (positions.length > 0) {
        map.fitBounds(L.latLngBounds(positions), {
          padding: [35, 35],
          maxZoom: 9,
        });
      }
      }, [map, positions]);

    return null;
  }

  export default function RouteMap({
    routes,
    selectedRoute,
    heatmapPoints,
  }: Props) {
    const route = selectedRoute ?? routes[0];

    if (!route || route.geometry.coordinates.length === 0) {
      return <div className="map-placeholder">Route map will appear here.</div>;
    }

    const positions = route.geometry.coordinates.map(
      ([longitude, latitude]) =>
        [latitude, longitude] as [number, number],
    );

    const heatmapSegments = heatmapPoints.slice(0, -1).map(
      (point, index) => {
        const nextPoint = heatmapPoints[index + 1];

        return {
          id: point.sequence,
          positions: [
            [point.latitude, point.longitude],
            [nextPoint.latitude, nextPoint.longitude],
          ] as [number, number][],
          risk: point.risk_level,
        };
      },
  );

  return (
    <MapContainer
      key={route.id}
      center={positions[0]}
      zoom={6}
      scrollWheelZoom
      className="route-map"
    >
      <FitRouteBounds positions={positions} />
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* {routes
        .filter((item) => item.id !== route.id)
        .map((item) => (
          <Polyline
            key={item.id}
            positions={item.geometry.coordinates.map(
              ([longitude, latitude]) =>
                [latitude, longitude] as [number, number],
            )}
            pathOptions={{
              color: "#94a3b8",
              weight: 4,
              opacity: 0.5,
            }}
          />
        ))}

      <Polyline
        positions={positions}
        pathOptions={{
          color: "#2563eb",
          weight: 5,
          opacity: 0.65,
        }}
      /> */}
      {heatmapSegments.length > 0 ? (
        heatmapSegments.map((segment) => (
          <Polyline
            key={segment.id}
            positions={segment.positions}
            pathOptions={{
              color: riskColors[segment.risk],
              weight: 6,
              opacity: 0.9,
            }}
          />
        ))
      ) : (
        <Polyline
          positions={positions}
          pathOptions={{
            color: "#2563eb",
            weight: 5,
            opacity: 0.8,
          }}
        />
      )}

      {heatmapPoints.map((point) => (
        <CircleMarker
          key={point.sequence}
          center={[point.latitude, point.longitude]}
          radius={8}
          pathOptions={{
            color: riskColors[point.risk_level],
            weight: 1,
            fillColor: riskColors[point.risk_level],
            fillOpacity: 0.75,
          }}
        >
          <Popup>
            <strong>
              Heatmap point — {point.distance_from_origin_miles.toFixed(1)} mi
            </strong>
            <br />
            Risk: {point.risk_level.replace("_", " ")}
            <br />
            Temperature: {point.temperature_f ?? "N/A"} °F
            <br />
            Wind: {point.wind_speed_mph ?? "N/A"} mph
            <br />
            Rain: {point.precipitation_in_per_hour ?? "N/A"} in/hr
            <br />
            Snow: {point.snowfall_in_per_hour ?? "N/A"} in/hr
            <br />
            {point.risk_reason}
          </Popup>
        </CircleMarker>
      ))}
      <RiskLegend />
    </MapContainer>
  );
}
