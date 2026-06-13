import useQuery from "@tanstack/react-query";
import analysisClient from "../api/analysisClient";

//fetches the list of analyses from GET /api/analyses/ and returns them.
function useAnalysisStatus() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["analysis", analysisId],
    queryFn: async () => {
      return analysisClient
        .get("/api/analysis" + analysisId)
        .then((res) => res.data);
    },
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "completed" || status === "failed" ? false : 2000; // Refetch every 2 seconds if the analysis is not completed or failed
    },
    enabled: !!analysisId, //0nly run the query if analysisId is provided
  });
}

function useAnalysisResults(analysisId, isCompleted) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["analysis-results", analysisId],
    queryFn: async () => {
      return analysisClient
        .get("/api/analysis/" + analysisId + "/results")
        .then((res) => res.data);
    },
    enabled: isCompleted && !!analysisId, // Only run the query if the analysis is completed
  });
}

export { useAnalysisStatus, useAnalysisResults };
