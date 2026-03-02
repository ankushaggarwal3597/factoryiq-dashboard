export default function Filters({ workers, stations, setWorker, setStation }) {
  return (
    <div className="flex flex-wrap gap-4 mb-6">
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-500 uppercase tracking-wide">
          Filter by Worker
        </label>
        <select
          onChange={(e) => setWorker(e.target.value)}
          className="border border-gray-200 bg-white px-3 py-2 rounded-lg text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Workers</option>
          {workers.map((w) => (
            <option key={w.worker_id} value={w.worker_id}>
              {w.name} — {w.role}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-500 uppercase tracking-wide">
          Filter by Station
        </label>
        <select
          onChange={(e) => setStation(e.target.value)}
          className="border border-gray-200 bg-white px-3 py-2 rounded-lg text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Stations</option>
          {stations.map((s) => (
            <option key={s.station_id} value={s.station_id}>
              {s.name} — {s.station_type}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}