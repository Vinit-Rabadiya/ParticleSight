import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Shows a scatter plot of anomaly scores — blue = normal, red = anomaly
// Props: anomalyData (anomaly_summary object from API)
export default function AnomalyScatterPlot({ anomalyData }) {
  const {
    anomaly_scores,
    anomaly_indices,
    total_events,
    total_anomalies,
    anomaly_percentage,
  } = anomalyData;

  // Build a Set for fast anomaly lookup
  const anomalySet = new Set(anomaly_indices);

  // Sample every 10th point — 10,000 dots is too many for the browser
  const normalPoints = [];
  const anomalyPoints = [];

  anomaly_scores.forEach((score, index) => {
    if (index % 10 !== 0) return;
    const point = { index, score: Number(score.toFixed(4)) };
    if (anomalySet.has(index)) {
      anomalyPoints.push(point);
    } else {
      normalPoints.push(point);
    }
  });

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      {/* Header + stats */}
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-800">
          Anomaly Detection
        </h3>
        <div className="text-right text-sm text-gray-500">
          <span className="font-medium text-red-600">{total_anomalies.toLocaleString()}</span>
          {" anomalies "}
          <span className="text-gray-400">({anomaly_percentage}%)</span>
          {" of "}
          {total_events.toLocaleString()} events
        </div>
      </div>

      {/* Scatter chart */}
      <ResponsiveContainer width="100%" height={280}>
        <ScatterChart margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
          <XAxis
            dataKey="index"
            name="Event"
            type="number"
            tick={{ fontSize: 10 }}
            label={{ value: "Event Index", position: "insideBottom", offset: -2, fontSize: 11 }}
          />
          <YAxis
            dataKey="score"
            name="Score"
            type="number"
            tick={{ fontSize: 10 }}
            label={{ value: "Anomaly Score", angle: -90, position: "insideLeft", fontSize: 11 }}
          />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            formatter={(value, name) => [value, name]}
          />
          <Legend />
          <Scatter
            name="Normal"
            data={normalPoints}
            fill="#3b82f6"
            opacity={0.3}
            r={2}
          />
          <Scatter
            name="Anomaly"
            data={anomalyPoints}
            fill="#ef4444"
            opacity={0.8}
            r={4}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
