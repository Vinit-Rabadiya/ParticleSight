import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function AnomalyScatterPlot({ anomalyData }) {
  // Convert to Set for fast lookup
  const anomalySet = new Set(anomalyData.anomaly_indices);

  // Sample every 10th point to keep the chart fast
  const normalPoints = [];
  const anomalyPoints = [];

  anomalyData.anomaly_scores.forEach((score, index) => {
    if (index % 10 !== 0) return; // only keep every 10th point
    const point = { index, score };
    if (anomalySet.has(index)) {
      anomalyPoints.push(point);
    } else {
      normalPoints.push(point);
    }
  });

    return (
    <div className="rounded-lg border bg-white p-4 shadow">
      <h1 className="text-lg font-semibold">Anomaly Detection</h1>
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart>
          <XAxis dataKey="index" />
          <YAxis dataKey="score" />
          <Tooltip />
          <Legend />
          <Scatter name="Normal" data={normalPoints} fill="#3B82F6" opacity={0.4} />
          <Scatter name="Anomaly" data={anomalyPoints} fill="#EF4444" opacity={.8}/>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AnomalyScatterPlot;