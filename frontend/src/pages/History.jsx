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

  if (isLoading) {
    return <div className="p-6 text-center">Loading analysis history...</div>;
  }

  if (isError) {
    return (
      <div className="p-6 text-center text-red-600">
        Failed to load analysis history.
      </div>
    );
  }

  const getStatusColor = (status) => {
    if (status === "completed") {
      return "bg-green-100 text-green-800";
    }

    if (status === "running") {
      return "bg-yellow-100 text-yellow-800";
    }

    if (status === "failed") {
      return "bg-red-100 text-red-800";
    }

    return "bg-gray-100 text-gray-800";
  };

  return (
    <div className="rounded-lg bg-white p-6 shadow">
      <h1 className="mb-6 text-2xl font-bold">Analysis History</h1>

      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            <th className="border border-gray-200 px-4 py-2 text-left">
              Dataset ID
            </th>

            <th className="border border-gray-200 px-4 py-2 text-left">Date</th>

            <th className="border border-gray-200 px-4 py-2 text-left">
              Status
            </th>

            <th className="border border-gray-200 px-4 py-2 text-left">
              Action
            </th>
          </tr>
        </thead>

        <tbody>
          {analyses.map((analysis) => (
            <tr key={analysis.id}>
              <td className="border border-gray-200 px-4 py-2">
                {analysis.dataset_id}
              </td>

              <td className="border border-gray-200 px-4 py-2">
                {analysis.triggered_at
                  ? new Date(analysis.triggered_at).toLocaleString()
                  : "N/A"}
              </td>

              <td className="border border-gray-200 px-4 py-2">
                <span
                  className={`rounded-full px-2 py-1 text-xs font-medium ${getStatusColor(
                    analysis.status,
                  )}`}
                >
                  {analysis.status}
                </span>
              </td>

              <td className="border border-gray-200 px-4 py-2">
                <button
                  onClick={() => navigate(`/dashboard/${analysis.id}`)}
                  className="rounded bg-blue-600 px-3 py-1 text-white hover:bg-blue-700"
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default History;
