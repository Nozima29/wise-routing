
import api from "./client";
import type { Trip, TripRequest, HeatmapResponse } from "../types/trip";


export async function createTrip(data: TripRequest): Promise<Trip> {
  const response = await api.post<Trip>("/trips/", data);
  return response.data;
}

export async function planTrip(id: number): Promise<Trip> {
  const response = await api.post<Trip>(`/trips/${id}/plan/`);
  return response.data;
}

export async function getTrip(id: number): Promise<Trip> {
  const response = await api.get<Trip>(`/trips/${id}/`);
  return response.data;
}

export async function getTripHeatmap(
  tripId: number,
  routeId: number,
  offsetHours: number,
): Promise<HeatmapResponse> {
  const response = await api.get<HeatmapResponse>(
    `/trips/${tripId}/heatmap/`,
    {
      params: {
        route_id: routeId,
        offset_hours: offsetHours,
      },
    },
  );

  return response.data;
}
