import { useParams } from "react-router-dom";
import { useAnalysisStatus, useAnalysisResults } from "../hooks/useAnalysis";
import DistributionChart from "../components/DistributionChart";
import CorrelationMatrix from "../components/CorrelationMatrix";

function Dashboard() {
  const { analysisId } = useParams();
  const { data: statusData } = useAnalysisStatus(analysisId);
  const isCompleted = statusData?.status === "completed";
  const { data: results, isLoading } = useAnalysisResults(
    analysisId,
    isCompleted,
  );

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
    return (
      <div className="grid grid-cols-3 gap-6">
        {/* Left 2/3 — charts */}
        <div className="col-span-2 flex flex-col gap-6">
          {/* Distribution charts */}
          {results.distribution_charts.map((chart, i) => (
            <DistributionChart
              key={i}
              columnName={chart.column_name}
              data={chart.data}
              isUnusual={chart.is_unusual}
            />
          ))}
          {/* Correlation matrix */}
          <CorrelationMatrix correlations={results.correlations} />
          {/* Anomaly scatter plot */}
        </div>
        {/* Right 1/3 — AI insights */}
        <div className="col-span-1 flex flex-col gap-4">
          {results.ai_insights.map((insight, i) => (
            <InsightCard key={i} insight={insight} />
          ))}
        </div>
      </div>
    );
  }
}
export default Dashboard;
