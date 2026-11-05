import { CloudSun, Truck, AlertCircle } from "lucide-react";

import TripForm from "./components/TripForm";
import RouteCard from "./components/RouteCard";
import RouteMap from "./components/RouteMap";
import HeatmapControls from "./components/HeatmapControls";

import { createTrip, planTrip, getTripHeatmap } from "./api/trips";
import type { Trip, TripRequest, Route, HeatmapResponse } from "./types/trip";
import { useEffect, useState } from "react";
import L from "leaflet";


function App() {
  const [trip, setTrip] = useState<Trip | null>(null);
  const [selectedRouteId, setSelectedRouteId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [heatmap, setHeatmap] = useState<HeatmapResponse | null>(null);
  const [forecastOffset, setForecastOffset] = useState(0);
  const [appliedOffset, setAppliedOffset] = useState(0);
  const [heatmapLoading, setHeatmapLoading] = useState(false);
  const [heatmapError, setHeatmapError] = useState("");

  const selectedRoute: Route | null =
    trip?.routes.find((route) => route.id === selectedRouteId)
    ?? trip?.routes.find((route) => route.is_recommended)
    ?? trip?.routes[0]
    ?? null;

  useEffect(() => {
    if (!trip || !selectedRoute) return;

    loadHeatmap(
      trip.id,
      selectedRoute.id,
      appliedOffset,
    );

    // The API request depends on the selected trip, route,
    // and committed forecast hour.
  }, [trip?.id, selectedRoute?.id, appliedOffset]);
  
  async function handlePlanTrip(data: TripRequest) {
    setLoading(true);
    setError("");
    setTrip(null);
    setSelectedRouteId(null);

    try {
      const createdTrip = await createTrip(data);
      const plannedTrip = await planTrip(createdTrip.id);

      setTrip(plannedTrip);

      const recommended = plannedTrip.routes.find(
        (route) => route.is_recommended
      );

      setSelectedRouteId(
        recommended?.id ?? plannedTrip.routes[0]?.id ?? null
      );
    } catch (err: any) {
      const message =
        err.response?.data?.error ??
        err.response?.data?.detail ??
        "Unable to plan this trip. Please check your inputs and try again.";

      setError(message);
    } finally {
      setLoading(false);
      setHeatmap(null);
      setForecastOffset(0);
      setAppliedOffset(0);
    }
  }

  async function loadHeatmap(
    tripId: number,
    routeId: number,
    offset: number,
  ) {
    setHeatmapLoading(true);
    setHeatmapError("");

    try {
      const result = await getTripHeatmap(
        tripId,
        routeId,
        offset,
      );

      setHeatmap(result);
    } catch (err: any) {
      setHeatmapError(
        err.response?.data?.detail ??
        "Unable to load weather forecast.",
      );
    } finally {
      setHeatmapLoading(false);
    }
}

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <Truck size={21} />
          </div>
          <div>
            <strong>RouteWise</strong>
            <span>Weather-aware truck routing</span>
          </div>
        </div>

        <div className="topbar-status">
          <span className="status-dot" />
          Routing system
        </div>
      </header>

      <main className="main-content">
        <section className="page-heading">
          <div>
            <span className="eyebrow">SMART TRANSPORTATION</span>
            <h1>Plan safer journeys.</h1>
            <p>
              Compare alternative routes using weather forecasts,
              cargo weight, and estimated travel time.
            </p>
          </div>
          <div className="weather-decoration">
            <CloudSun size={42} />
          </div>
        </section>

        <div className="workspace">
          <aside className="sidebar">
            <TripForm onSubmit={handlePlanTrip} loading={loading} />

            {error && (
              <div className="error-message">
                <AlertCircle size={18} />
                <span>{error}</span>
              </div>
            )}
          </aside>

          <section className="results">
            <div className="section-heading">
              <div>
                <span className="eyebrow">ROUTE ANALYSIS</span>
                <h2>Route alternatives</h2>
              </div>

              {trip && (
                <span className="result-count">
                  {trip.routes.length} routes found
                </span>
              )}
            </div>

            {loading && (
              <div className="loading-panel">
                <div className="loader" />
                <h3>Analyzing your journey</h3>
                <p>
                  Finding routes and checking weather conditions
                  along the way. This may take a little while.
                </p>
              </div>
            )}

            {!loading && !trip && (
              <div className="empty-state">
                <div className="empty-icon">
                  <CloudSun size={34} />
                </div>
                <h3>Your route analysis starts here</h3>
                <p>
                  Enter your journey details to compare routes,
                  forecast conditions, and travel risks.
                </p>
              </div>
            )}

            {!loading && trip && (
              <>
                <div className="route-list">
                  {trip.routes.map((route) => (
                    <RouteCard
                      key={route.id}
                      route={route}
                      selected={selectedRoute?.id === route.id}
                      onClick={() => setSelectedRouteId(route.id)}
                    />
                  ))}
                </div>

                {trip.routes.length === 0 && (
                  <div className="empty-state">
                    <h3>No routes returned</h3>
                    <p>
                      The routing provider did not return any alternatives.
                    </p>
                  </div>
                )}

                {trip.routes.length > 0 && (
                  <div className="map-section">
                    <div className="section-heading">
                      <div>
                        <span className="eyebrow">GEOGRAPHIC VIEW</span>
                        <h2>Route map</h2>
                      </div>
                      <span className="selected-label">
                        {selectedRoute?.is_recommended
                          ? "Recommended route"
                          : "Selected route"}
                      </span>
                    </div>

                    {/* <RouteMap
                      routes={trip.routes}
                      selectedRoute={selectedRoute}
                    /> */}
                    <HeatmapControls
                      value={forecastOffset}
                      onChange={setForecastOffset}
                      onApply={() => setAppliedOffset(forecastOffset)}
                      loading={heatmapLoading}
                      forecastTime={heatmap?.forecast_time}
                    />

                    {heatmapError && (
                      <div className="error-message">
                        {heatmapError}
                      </div>
                    )}

                    {heatmapLoading && (
                      <p className="map-loading">
                        Updating weather conditions along the route...
                      </p>
                    )}

                    <RouteMap
                      routes={trip.routes}
                      selectedRoute={selectedRoute}
                      heatmapPoints={heatmap?.points ?? []}
                    />

                    <div className="map-legend">
                      <span><i className="legend-dot low" /> Low</span>
                      <span><i className="legend-dot moderate" /> Moderate</span>
                      <span><i className="legend-dot high" /> High</span>
                      <span><i className="legend-dot severe" /> Severe</span>
                      <span><i className="legend-dot no-travel" /> No Travel</span>
                    </div>
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
