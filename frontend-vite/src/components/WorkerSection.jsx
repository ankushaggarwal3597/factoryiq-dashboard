function fmtHours(secs) {
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  return `${h}h ${m}m`;
}

function UtilBadge({ pct }) {
  const color =
    pct >= 75
      ? "bg-emerald-100 text-emerald-700"
      : pct >= 50
      ? "bg-amber-100 text-amber-700"
      : "bg-red-100 text-red-600";
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${color}`}>
      {pct}%
    </span>
  );
}

export default function WorkerSection({ workers }) {
  if (!workers.length) {
    return (
      <div className="bg-white shadow rounded-xl p-5">
        <h2 className="text-xl font-semibold mb-4">Worker Productivity</h2>
        <p className="text-gray-400 text-sm">No worker data available.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-xl p-5">
      <h2 className="text-xl font-semibold mb-4">Worker Productivity</h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm border-separate border-spacing-y-2">
          <thead>
            <tr className="border-b text-left text-xs text-gray-400 uppercase tracking-wide">
              <th className="pb-3 pr-4">Worker</th>
              <th className="pb-3 pr-4">Role</th>
              <th className="pb-3 pr-4">Active Time</th>
              <th className="pb-3 pr-4">Idle Time</th>
              <th className="pb-3 pr-4">Utilization</th>
              <th className="pb-3 pr-4">Units</th>
              <th className="pb-3">Units/hr</th>
            </tr>
          </thead>
          <tbody>
            {workers.map((w) => (
              <tr key={w.worker_id} className="border-b last:border-0 bg-slate-50 hover:bg-blue-50 rounded-lg">
                <td className="py-3 pr-4 font-medium text-gray-800">{w.name}</td>
                <td className="py-3 pr-4 text-gray-500">{w.role}</td>
                <td className="py-3 pr-4 font-mono text-gray-700">
                  {fmtHours(w.active_time_secs)}
                </td>
                <td className="py-3 pr-4 font-mono text-gray-500">
                  {fmtHours(w.idle_time_secs)}
                </td>
                <td className="py-3 pr-4">
                  <UtilBadge pct={w.utilization_pct} />
                </td>
                <td className="py-3 pr-4 font-mono font-semibold text-gray-800">
                  {w.total_units}
                </td>
                <td className="py-3 font-mono text-gray-600">{w.units_per_hour}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}