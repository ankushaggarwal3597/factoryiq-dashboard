import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
} from "recharts";

const COLORS = ["#2563eb", "#16a34a", "#d97706", "#dc2626", "#7c3aed", "#0891b2"];

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-4 py-3 text-sm">
      <p className="font-semibold text-gray-700 mb-1">{label}</p>
      <p className="text-blue-600">
        Utilization: <strong>{payload[0].value}%</strong>
      </p>
    </div>
  );
}

export default function UtilizationChart({ workers }) {
  if (!workers.length) return null;

  const data = workers.map((w) => ({
    name: w.name.split(" ")[0], // first name only for chart
    utilization_pct: w.utilization_pct,
    units: w.total_units,
  }));

  return (
    <div className="bg-white p-5 rounded-xl shadow mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Worker Utilization</h2>
        <span className="text-xs text-gray-400 uppercase tracking-wide">
          % of active vs total logged time
        </span>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} barCategoryGap="30%">
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12, fill: "#6b7280" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 12, fill: "#6b7280" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="utilization_pct" radius={[4, 4, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}