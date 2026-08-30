import { useQuery } from "@tanstack/react-query";
import client from "../api/client";

// Polls GET /api/analysis/{id} every 2 seconds until status is completed or failed
export function useAnalysisStatus(analysisId) {
  return useQuery({
    queryKey: ["analysis", analysisId],
    queryFn: async () => {
      const response = await client.get(`/api/analysis/${analysisId}`);
      return response.data;
    },
    enabled: !!analysisId, // don't run if analysisId is empty
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      // stop polling once done
      if (status === "completed" || status === "failed") return false;
      return 2000; // poll every 2 seconds
    },
  });
}

// Fetches full results from GET /api/analysis/{id}/results
// Only runs when isCompleted is true
export function useAnalysisResults(analysisId, isCompleted) {
  return useQuery({
    queryKey: ["analysis-results", analysisId],
    queryFn: async () => {
      const response = await client.get(`/api/analysis/${analysisId}/results`);
      return response.data;
    },
    enabled: !!analysisId && isCompleted,
  });
}
