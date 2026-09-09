import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Custom tooltip — shows anomaly reason for red points, basic info for blue
function AnomalyTooltip({ active, payload, pointExplanations }) {
  if (!active || !payload?.length) return null;
  const point = payload[0]?.payload;
  if (!point) return null;

  const explanation = pointExplanations?.[point.index];

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-xs max-w-xs">
      <p className="font-semibold text-gray-700 mb-1">
        Event #{point.index}
      </p>
      <p className="text-gray-500 mb-2">
        Anomaly score: <span className="font-medium text-red-600">{point.score}</span>
      </p>

      {explanation ? (
        <div>
          <p className="font-medium text-red-700 mb-1">Why it was flagged:</p>
          {explanation.map((d, i) => (
            <div key={i} className="mb-1 border-t border-gray-100 pt-1">
              <span className="font-medium text-gray-800">{d.feature}</span>
              {" = "}{d.value}
              <span className={`ml-1 font-medium ${d.direction === "high" ? "text-red-500" : "text-blue-500"}`}>
                ({d.direction}, {d.z_score}σ from normal)
              </span>
              <div className="text-gray-400">Normal avg: {d.normal_mean}</div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-400 italic">Normal event</p>
      )}
    </div>
  );
}

export default function AnomalyScatterPlot({ anomalyData }) {
  const {
    anomaly_scores,
    anomaly_indices,
    total_events,
    total_anomalies,
    anomaly_percentage,
    point_explanations,
  } = anomalyData;

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
      <div className="flex items-start justify-between mb-1">
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

      {/* Explanation hint */}
      <p className="text-xs text-gray-400 mb-4">
        Hover a <span className="text-red-500 font-medium">red point</span> to see which features made it anomalous.
        Score closer to <span className="font-medium">−1</span> = more anomalous.
      </p>

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
            content={<AnomalyTooltip pointExplanations={point_explanations} />}
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

      {/* Most anomalous features summary */}
      {anomalyData.most_anomalous_features?.length > 0 && (
        <div className="mt-4 border-t border-gray-100 pt-4">
          <p className="text-xs font-medium text-gray-600 mb-2">
            Features most different in anomalous events:
          </p>
          <div className="flex flex-wrap gap-2">
            {anomalyData.most_anomalous_features.map((f, i) => (
              <div key={i} className="bg-red-50 border border-red-100 rounded-lg px-3 py-1.5 text-xs">
                <span className="font-medium text-red-700">{f.feature}</span>
                <span className="text-gray-500 ml-1">
                  anomaly avg {f.anomaly_mean} vs normal {f.normal_mean}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
