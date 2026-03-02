import { useEffect, useState, useCallback } from "react";
import {
  fetchFactoryMetrics,
  fetchWorkers,
  fetchStations,
  seedFactory,
} from "../api/api";

import FactorySummary from "../components/FactorySummary";
import WorkerSection from "../components/WorkerSection";
import StationSection from "../components/StationSection";
import UtilizationChart from "../components/UtilizationChart";
import Filters from "../components/Filters";

import { RefreshCcw, Database } from "lucide-react";

export default function Dashboard() {
  const [factory, setFactory] = useState(null);
  const [workers, setWorkers] = useState([]);
  const [stations, setStations] = useState([]);

  const [workerFilter, setWorker] = useState("");
  const [stationFilter, setStation] = useState("");

  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setError(null);

    try {
      const [f, w, s] = await Promise.all([
        fetchFactoryMetrics(),
        fetchWorkers(workerFilter),
        fetchStations(stationFilter),
      ]);

      setFactory(f.data);
      setWorkers(w.data);
      setStations(s.data);
    } catch {
      setError("Backend not reachable.");
    } finally {
      setLoading(false);
    }
  }, [workerFilter, stationFilter]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSeed() {
    setSeeding(true);
    await seedFactory();
    await load();
    setSeeding(false);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200">

      {/* HEADER */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-8 py-6 flex justify-between items-center">

          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              FactoryIQ Dashboard
            </h1>

            <p className="text-sm text-slate-500 mt-1">
              AI CCTV Productivity Intelligence
            </p>
          </div>

          <div className="flex gap-3">

            <button
              onClick={load}
              className="flex items-center gap-2 bg-white border px-4 py-2 rounded-lg shadow hover:bg-gray-50"
            >
              <RefreshCcw size={16}/>
              Refresh
            </button>

            <button
              onClick={handleSeed}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-700"
            >
              <Database size={16}/>
              {seeding ? "Generating..." : "Generate Shift"}
            </button>

          </div>

        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-8">

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {loading ? (
          <div className="h-64 flex items-center justify-center text-gray-400">
            Loading Factory Metrics...
          </div>
        ) : (
          <>
            <Filters
              workers={workers}
              stations={stations}
              setWorker={setWorker}
              setStation={setStation}
            />

            <FactorySummary data={factory} />

            <UtilizationChart workers={workers} />

            <div className="grid lg:grid-cols-2 gap-6 mt-6">
              <WorkerSection workers={workers}/>
              <StationSection stations={stations}/>
            </div>
          </>
        )}
      </div>
    </div>
  );
}