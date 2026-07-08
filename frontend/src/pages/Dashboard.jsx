import { useParams } from "react-router-dom";
import { useAnalysisStatus, useAnalysisResults } from "../hooks/useAnalysis";
import DistributionChart from "../components/DistributionChart";
import CorrelationMatrix from "../components/CorrelationMatrix";
import AnomalyScatterPlot from "../components/AnomalyScatterPlot";
import InsightCard from "../components/InsightCard";

function getFallbackReferenceUrl(columnName) {
  return `https://opendata.cern.ch/search?q=${encodeURIComponent(columnName || "")}`;
}

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
    const aiInsights = results.ai_insights || [];
    const overviewInsight = aiInsights.find((insight) =>
      String(insight?.title || "")
        .toLowerCase()
        .includes("dataset at a glance"),
    );
    const columnMeaningsInsight =
      aiInsights.find((insight) =>
        String(insight?.title || "")
          .toLowerCase()
          .includes("column meanings"),
      ) ||
      aiInsights.find((insight) => {
        const explanation = String(insight?.explanation || "");
        const hasBulletLines = explanation
          .split("\n")
          .some((line) => line.trim().startsWith("-"));
        const hasSource = /(?:Source|source):\s*https?:\/\//.test(explanation);
        return hasBulletLines && hasSource;
      });
    const columnGuideInsight = aiInsights.find((insight) =>
      String(insight?.title || "")
        .toLowerCase()
        .includes("column guide"),
    );

    const distributionCharts = Object.entries(results.distributions || {}).map(
      ([columnName, stats]) => ({
        columnName,
        data: stats.histogram,
        isUnusual: stats.is_unusual,
      }),
    );

    const columnPreview = Object.keys(results.distributions || {}).slice(0, 8);
    let columnMeaningLines = (columnMeaningsInsight?.explanation || "")
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.startsWith("-"));

    const hasFallbackPlaceholder = columnMeaningLines.some((line) =>
      line.toLowerCase().includes("fallback mode"),
    );

    if (hasFallbackPlaceholder) {
      columnMeaningLines = [];
    }

    const columnMeaningItems = columnMeaningLines.map((line) => {
      const cleanLine = line.replace(/^[-]\s*/, "").trim();
      const sourceMatch = cleanLine.match(
        /(?:Source|source):\s*(https?:\/\/\S+)/,
      );
      const sourceUrl = sourceMatch ? sourceMatch[1].trim() : "";
      const withoutSource = cleanLine
        .replace(/(?:Source|source):\s*https?:\/\/\S+\s*$/i, "")
        .trim();
      const separatorIndex = cleanLine.indexOf(":");

      const columnName =
        separatorIndex >= 0
          ? withoutSource.slice(0, separatorIndex).trim()
          : cleanLine.split(" ")[0]?.trim();
      const meaningText =
        separatorIndex >= 0
          ? withoutSource.slice(separatorIndex + 1).trim()
          : withoutSource;

      return {
        columnName,
        meaningText,
        referenceUrl: sourceUrl || getFallbackReferenceUrl(columnName),
      };
    });

    return (
      <div className="space-y-6">
        <section className="rounded-xl border border-emerald-100 bg-emerald-50 p-4 text-sm text-emerald-900">
          <h2 className="text-base font-semibold">Dataset Overview</h2>
          <p className="mt-2">
            {overviewInsight?.explanation ||
              `This dataset contains ${results?.anomaly_summary?.total_events || 0} events and ${Object.keys(results.distributions || {}).length} numeric columns used for analysis.`}
          </p>
          <p className="mt-2">
            {columnGuideInsight?.explanation ||
              `Key columns include: ${columnPreview.join(", ") || "No numeric columns detected"}.`}
          </p>

          <div className="mt-3">
            <h3 className="font-semibold">What Each Column Means</h3>
            {columnMeaningItems.length > 0 ? (
              <ul className="mt-1 list-disc space-y-1 pl-5">
                {columnMeaningItems.map((item, index) => (
                  <li key={`${item.columnName}-${index}`}>
                    <span className="font-medium">{item.columnName}</span>
                    {": "}
                    <span>{item.meaningText}</span>{" "}
                    <a
                      className="underline"
                      href={item.referenceUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Learn exact definition
                    </a>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-1 text-amber-900">
                AI-generated physics meanings were unavailable for this
                analysis. Run a new analysis to regenerate this section.
              </p>
            )}
          </div>
        </section>

        <section className="rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm text-blue-900">
          <h2 className="text-base font-semibold">How To Read These Results</h2>
          <div className="mt-2 grid gap-2 md:grid-cols-2">
            <p>
              <strong>Surprise score (out of 10):</strong> higher means more
              unexpected.
            </p>
            <p>
              <strong>Unusual Distribution badge:</strong> this variable has an
              uncommon shape.
            </p>
            <p>
              <strong>Correlation (r value):</strong> near +1 is strong
              positive, near -1 is strong negative.
            </p>
            <p>
              <strong>Anomaly chart:</strong> red points are unusual events,
              blue points are normal events.
            </p>
          </div>
        </section>

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
            {aiInsights.map((insight, i) => (
              <InsightCard key={i} insight={insight} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return null;
}
export default Dashboard;
