import useQuery from "@tanstack/react-query";
import client from "../api/client";

//fetches the list of datasets from GET /api/datasets/ and returns them.
function useDatasets() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["datasets"],
    queryFn: async () => {
      return client.get("/datasets").then((res) => res.data);
    },
  });
}

export default useDatasets;