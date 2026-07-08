import { useQuery } from "@tanstack/react-query";
import client from "../api/client";

//fetches the list of analyses from GET /api/analyses/ and returns them.
function useAnalysisStatus(analysisId) {
  return useQuery({
    queryKey: ["analysis", analysisId],

    queryFn: async () => {
      const response = await client.get(`/api/analysis/${analysisId}`);

      return response.data;
    },
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "completed" || status === "failed" ? false : 2000; // Refetch every 2 seconds if the analysis is not completed or failed
    },
    enabled: !!analysisId, //0nly run the query if analysisId is provided
  });
}

function useAnalysisResults(analysisId, isCompleted) {
  return useQuery({
    queryKey: ["analysis-results", analysisId],
    queryFn: async () => {
      return client
        .get("/api/analysis/" + analysisId + "/results")
        .then((res) => res.data);
    },
    enabled: isCompleted && !!analysisId, // Only run the query if the analysis is completed
  });
}

export { useAnalysisStatus, useAnalysisResults };
