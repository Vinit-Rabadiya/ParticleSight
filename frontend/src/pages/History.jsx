import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

function History() {
  const navigate = useNavigate();

  const {
    data: analyses = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["analysis-history"],
    queryFn: async () => {
      const response = await client.get("/api/analysis/");
      return response.data;
    },
  });

  // Fetch datasets so we can show names instead of raw IDs
  const { data: datasets = [] } = useQuery({
    queryKey: ["datasets"],
    queryFn: async () => {
      const response = await client.get("/api/datasets/");
      return response.data;
    },
  });

  const datasetMap = Object.fromEntries(datasets.map((d) => [d.id, d]));

  function getStatusStyle(status) {
    if (status === "completed") return "bg-green-100 text-green-800";
    if (status === "running") return "bg-yellow-100 text-yellow-800";
    if (status === "failed") return "bg-red-100 text-red-800";
    return "bg-gray-100 text-gray-600";
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Analysis History</h1>
        <p className="text-sm text-gray-500 mt-1">
          All past analysis runs — click View to open results.
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center gap-3 text-gray-500 py-12 justify-center">
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          Loading history...
        </div>
      )}

      {isError && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
          Could not load analysis history. Make sure the backend is running.
        </div>
      )}

      {!isLoading && !isError && analyses.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 rounded-lg px-4 py-3 text-sm">
          No analyses yet. Go to the home page and run one.
        </div>
      )}

      {!isLoading && !isError && analyses.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-5 py-3 text-gray-500 font-medium">
                  Dataset
                </th>
                <th className="text-left px-5 py-3 text-gray-500 font-medium">
                  Date
                </th>
                <th className="text-left px-5 py-3 text-gray-500 font-medium">
                  Status
                </th>
                <th className="text-left px-5 py-3 text-gray-500 font-medium">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {analyses.map((analysis) => {
                const dataset = datasetMap[analysis.dataset_id];
                return (
                  <tr key={analysis.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3 text-gray-800">
                      <div className="font-medium">
                        {dataset?.name || `Dataset ${analysis.dataset_id}`}
                      </div>
                      {dataset?.experiment && (
                        <span className="text-xs text-gray-400">
                          {dataset.experiment}
                          {dataset.year ? ` · ${dataset.year}` : ""}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-gray-500">
                      {analysis.triggered_at
                        ? new Date(analysis.triggered_at).toLocaleString()
                        : "—"}
                    </td>
                    <td className="px-5 py-3">
                      <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusStyle(
                          analysis.status,
                        )}`}
                      >
                        {analysis.status}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <button
                        onClick={() => navigate(`/dashboard/${analysis.id}`)}
                        className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 transition-colors"
                      >
                        View →
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default History;
