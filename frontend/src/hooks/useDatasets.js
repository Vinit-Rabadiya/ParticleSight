import { useQuery } from "@tanstack/react-query";
import client from "../api/client";

//fetches the list of datasets from GET /api/datasets/ and returns them.
function useDatasets() {
  return useQuery({
    queryKey: ["datasets"],
    queryFn: async () => {
      const response = await client.get("/api/datasets/");
      return response.data;
    },
  });
}

export default useDatasets;
