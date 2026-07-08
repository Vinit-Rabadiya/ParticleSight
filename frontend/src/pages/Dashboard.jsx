import { useParams } from "react-router-dom";
import { useAnalysisStatus, useAnalysisResults } from "../hooks/useAnalysis";
import DistributionChart from "../components/DistributionChart";
import CorrelationMatrix from "../components/CorrelationMatrix";
import AnomalyScatterPlot from "../components/AnomalyScatterPlot";
import InsightCard from "../components/InsightCard";

function Dashboard() {
  const { analysisId } = useParams();
  const { data: statusData } = useAnalysisStatus(analysisId);
  const status = statusData?.status;
  const isCompleted = statusData?.status === "completed";
  const { data: results, isLoading } = useAnalysisResults(
    analysisId,
    isCompleted,
  );

  if (status === "failed") {
    return (
      <div className="mx-auto max-w-3xl rounded-xl border border-red-200 bg-red-50 p-6 text-red-800">
        <h2 className="text-xl font-semibold">Analysis failed</h2>
        <p className="mt-2 text-sm">
          {statusData?.error_message || "The analysis could not complete."}
        </p>
      </div>
    );
  }

  if (!isCompleted) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>

        <p className="mt-4 text-lg font-medium animate-pulse">
          Analysis running...
        </p>

        <p className="text-gray-500">
          Status: {statusData?.status ?? "starting"}
        </p>
      </div>
    );
  }

  if (isCompleted && isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
        <p className="mt-4 text-lg font-medium animate-pulse">
          Loading analysis results...
        </p>
      </div>
    );
  }

  if (isCompleted && results) {
    const distributionCharts = Object.entries(results.distributions || {}).map(
      ([columnName, stats]) => ({
        columnName,
        data: stats.histogram,
        isUnusual: stats.is_unusual,
      }),
    );

    return (
      <div className="grid grid-cols-3 gap-6">
        {/* Left 2/3 — charts */}
        <div className="col-span-2 flex flex-col gap-6">
          {/* Distribution charts */}
          {distributionCharts.map((chart, i) => (
            <DistributionChart
              key={i}
              columnName={chart.columnName}
              data={chart.data}
              isUnusual={chart.isUnusual}
            />
          ))}
          {/* Correlation matrix */}
          <CorrelationMatrix correlations={results.top_correlations || []} />
          {/* Anomaly scatter plot */}
          <AnomalyScatterPlot anomalyData={results.anomaly_summary} />
        </div>
        {/* Right 1/3 — AI insights */}
        <div className="col-span-1 flex flex-col gap-4">
          {(results.ai_insights || []).map((insight, i) => (
            <InsightCard key={i} insight={insight} />
          ))}
        </div>
      </div>
    );
  }

  return null;
}
export default Dashboard;
