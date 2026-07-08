import { useState } from "react";
import useDatasets from "../hooks/useDatasets";
import client from "../api/client";
import DatasetCard from "../components/DatasetCard";

function Home() {
  const { data: datasets = [], isLoading, isError, error } = useDatasets();
  const [cernLink, setCernLink] = useState("");
  const [statusMessage, setStatusMessage] = useState("");

  const handleAnalyse = async () => {
    const trimmedLink = cernLink.trim();

    if (!trimmedLink) {
      setStatusMessage("Please paste a CERN dataset link first.");
      return;
    }

    try {
      const res = await client.post("/api/analysis/", null, {
        params: { cern_link: trimmedLink },
      });
      setStatusMessage(`Analysis started. ${res.data.message}`);
    } catch (err) {
      setStatusMessage(
        err?.response?.data?.detail || "Failed to start analysis.",
      );
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-gray-900">Project Name</h1>
        <p className="mt-2 text-lg text-gray-600">
          Your project tagline goes here
        </p>
      </header>

      {!isLoading && !isError && (
        <div className="mb-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="flex-1">
              <label
                htmlFor="cern-link"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Paste a CERN dataset link
              </label>
              <input
                id="cern-link"
                type="url"
                value={cernLink}
                onChange={(event) => setCernLink(event.target.value)}
                placeholder="https://opendata.cern.ch/record/700/files/MuRun2010B_0.csv"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none"
              />
            </div>

            <button
              onClick={handleAnalyse}
              className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
              disabled={!cernLink.trim()}
            >
              Analyze
            </button>
          </div>

          {statusMessage && (
            <p className="mt-3 text-sm text-blue-700">{statusMessage}</p>
          )}
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading datasets...</p>
        </div>
      ) : isError ? (
        <div className="text-center py-12">
          <p className="text-red-600">
            {error?.message || "Failed to load datasets."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {datasets.map((dataset) => (
            <DatasetCard key={dataset.id} dataset={dataset} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Home;
