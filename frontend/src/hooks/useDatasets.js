import { useQuery } from "@tanstack/react-query";
import client from "../api/client";

// Fetches the list of all datasets from GET /api/datasets/
// Returns { data, isLoading, isError } from TanStack Query
export function useDatasets() {
  return useQuery({
    queryKey: ["datasets"],
    queryFn: async () => {
      const response = await client.get("/api/datasets/");
      return response.data;
    },
  });
}
