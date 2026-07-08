import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Label,
} from "recharts";

function DistributionChart({ columnName, data, isUnusual }) {
  const chartData = data.counts.map((count, i) => ({
    bin: data.bin_edges[i].toFixed(2),
    count: count,
  }));

  return (
    <div className="rounded-lg border bg-white p-4 shadow">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-lg font-semibold">
          {columnName}
          {isUnusual && (
            <span className="text-red-500 text-sm font-medium">⚠️</span>
          )}
        </h3>
        {isUnusual && (
          <span className="rounded-full bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-800">
            Unusual Distribution
          </span>
        )}
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="bin" tick={{ fontSize: 12 }}>
            <Label
              value={`${columnName} value range`}
              offset={-2}
              position="insideBottom"
            />
          </XAxis>
          <YAxis tick={{ fontSize: 12 }}>
            <Label
              value="Number of events"
              angle={-90}
              position="insideLeft"
              style={{ textAnchor: "middle" }}
            />
          </YAxis>
          <Tooltip />
          <Bar dataKey="count" fill="#3B82F6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default DistributionChart;
