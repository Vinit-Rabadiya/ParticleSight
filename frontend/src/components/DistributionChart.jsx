import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Label,
} from "recharts";

// Shows a histogram for one numeric column
// Props: columnName (string), data ({ counts, bin_edges }), isUnusual (bool)
export default function DistributionChart({ columnName, data, isUnusual }) {
  const chartData = data.counts.map((count, i) => ({
    bin: Number(data.bin_edges[i]).toFixed(2),
    count,
  }));

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {/* Column name + unusual flag */}
      <div className="flex items-center gap-2 mb-1">
        <span className="text-sm font-semibold text-gray-700">{columnName}</span>
        {isUnusual && (
          <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
            Unusual Distribution
          </span>
        )}
      </div>
      <p className="text-xs text-gray-400 mb-3">
        Distribution of values — bars show how many events fall in each range
      </p>

      <ResponsiveContainer width="100%" height={150}>
        <BarChart
          data={chartData}
          margin={{ top: 4, right: 10, left: 10, bottom: 30 }}
        >
          <XAxis
            dataKey="bin"
            tick={{ fontSize: 9 }}
            interval="preserveStartEnd"
          >
            <Label
              value={`${columnName} value`}
              position="insideBottom"
              offset={-18}
              style={{ fontSize: 10, fill: "#6b7280" }}
            />
          </XAxis>
          <YAxis tick={{ fontSize: 9 }}>
            <Label
              value="Event count"
              angle={-90}
              position="insideLeft"
              offset={10}
              style={{ fontSize: 10, fill: "#6b7280" }}
            />
          </YAxis>
          <Tooltip
            formatter={(value) => [value.toLocaleString(), "Events"]}
            labelFormatter={(label) => `Value: ${label}`}
          />
          <Bar dataKey="count" fill="#3b82f6" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
