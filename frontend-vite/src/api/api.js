import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api",
});

export const fetchFactoryMetrics = () =>
  API.get("/metrics/factory");

export const fetchWorkers = (workerId = "") =>
  API.get(`/metrics/workers${workerId ? `?worker_id=${workerId}` : ""}`);

export const fetchStations = (stationId = "") =>
  API.get(`/metrics/workstations${stationId ? `?station_id=${stationId}` : ""}`);

export const fetchRecentEvents = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return API.get(`/events/recent?${qs}`);
};

export const seedFactory = () =>
  API.post("/seed-dummy-data");

export const ingestEvent = (event) =>
  API.post("/events", event);

export default API;