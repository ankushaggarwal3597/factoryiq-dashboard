function fmtHours(secs) {
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  return `${h}h ${m}m`;
}

function UtilBar({ pct }) {
  const color =
    pct >= 75 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-400" : "bg-red-400";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
      <span className="text-xs font-mono text-gray-600 w-10 text-right">
        {pct}%
      </span>
    </div>
  );
}

export default function StationSection({ stations }) {
  if (!stations.length) {
    return (
      <div className="bg-white shadow rounded-xl p-5">
        <h2 className="text-xl font-semibold mb-4">Workstation Metrics</h2>
        <p className="text-gray-400 text-sm">No station data available.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-xl p-5">
      <h2 className="text-xl font-semibold mb-4">Workstation Metrics</h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-xs text-gray-400 uppercase tracking-wide">
              <th className="pb-3 pr-4">Station</th>
              <th className="pb-3 pr-4">Type</th>
              <th className="pb-3 pr-4">Occupancy</th>
              <th className="pb-3 pr-4 min-w-[140px]">Utilization</th>
              <th className="pb-3 pr-4">Units</th>
              <th className="pb-3">Throughput</th>
            </tr>
          </thead>
          <tbody>
            {stations.map((s) => (
              <tr key={s.station_id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="py-3 pr-4 font-medium text-gray-800">{s.name}</td>
                <td className="py-3 pr-4 text-gray-500">{s.station_type}</td>
                <td className="py-3 pr-4 font-mono text-gray-700">
                  {fmtHours(s.occupancy_time_secs)}
                </td>
                <td className="py-3 pr-4 min-w-[140px]">
                  <UtilBar pct={s.utilization_pct} />
                </td>
                <td className="py-3 pr-4 font-mono font-semibold text-gray-800">
                  {s.total_units}
                </td>
                <td className="py-3 font-mono text-gray-600">
                  {s.throughput_rate} u/hr
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}