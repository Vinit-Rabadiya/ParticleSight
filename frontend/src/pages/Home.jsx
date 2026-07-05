import useDatasets from "../hooks/useDatasets";
import useNavigation from "react-router-dom";
import client from "../api/client";
import DatasetCard from "../components/DatasetCard";

function Home() {
  const { data: datasets, isLoading, error } = useDatasets();

  const handleAnalyse = async (datasetId) => {
    const res = await client.post(`/api/analysis/? dataset_id=` + datasetId);
    return res.data;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-gray-900">Project Name</h1>
        <p className="mt-2 text-lg text-gray-600">
          Your project tagline goes here
        </p>
      </header>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading datasets...</p>
        </div>
      ) : isError ? (
        <div className="text-center py-12">
          <p className="text-red-600">Failed to load datasets.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {datasets.map((dataset) => (
            <DatasetCard
              key={dataset.id}
              dataset={dataset}
              onAnalyse={handleAnalyse}
            />
          ))}
        </div>
      )}
    </div>
  );
}
