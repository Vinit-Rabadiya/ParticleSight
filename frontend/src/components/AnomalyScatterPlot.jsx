import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label,
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
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="index" tick={{ fontSize: 12 }}>
            <Label value="Event index" position="insideBottom" offset={-2} />
          </XAxis>
          <YAxis dataKey="score" tick={{ fontSize: 12 }}>
            <Label
              value="Anomaly score"
              angle={-90}
              position="insideLeft"
              style={{ textAnchor: "middle" }}
            />
          </YAxis>
          <Tooltip />
          <Legend />
          <Scatter
            name="Normal"
            data={normalPoints}
            fill="#3B82F6"
            opacity={0.4}
          />
          <Scatter
            name="Anomaly"
            data={anomalyPoints}
            fill="#EF4444"
            opacity={0.8}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AnomalyScatterPlot;
