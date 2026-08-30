import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// Shows a histogram for one numeric column
// Props: columnName (string), data ({ counts, bin_edges }), isUnusual (bool)
export default function DistributionChart({ columnName, data, isUnusual }) {
  // Transform histogram data into the format Recharts expects
  const chartData = data.counts.map((count, i) => ({
    bin: Number(data.bin_edges[i]).toFixed(2),
    count,
  }));

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {/* Column name + unusual flag */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-sm font-semibold text-gray-700">
          {columnName}
        </span>
        {isUnusual && (
          <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
            Unusual
          </span>
        )}
      </div>

      {/* Bar chart */}
      <ResponsiveContainer width="100%" height={120}>
        <BarChart
          data={chartData}
          margin={{ top: 0, right: 0, left: -20, bottom: 0 }}
        >
          <XAxis
            dataKey="bin"
            tick={{ fontSize: 9 }}
            interval="preserveStartEnd"
          />
          <YAxis tick={{ fontSize: 9 }} />
          <Tooltip
            formatter={(value) => [value.toLocaleString(), "Count"]}
            labelFormatter={(label) => `Bin: ${label}`}
          />
          <Bar dataKey="count" fill="#3b82f6" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
