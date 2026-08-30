import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDatasets } from "../hooks/useDatasets";
import DatasetCard from "../components/DatasetCard";
import AddDatasetModal from "../components/AddDatasetModal";
import client from "../api/client";
import { useQueryClient } from "@tanstack/react-query";

export default function Home() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: datasets, isLoading, isError } = useDatasets();
  const [showModal, setShowModal] = useState(false);

  // Triggers analysis for a dataset and navigates to the dashboard
  async function handleAnalyse(datasetId) {
    try {
      const response = await client.post(
        `/api/analysis/?dataset_id=${datasetId}`
      );
      const analysisId = response.data.analysis_id;
      navigate(`/dashboard/${analysisId}`);
    } catch (err) {
      console.error("Failed to start analysis:", err);
      alert("Could not start analysis. Is the backend running?");
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Modal */}
      {showModal && (
        <AddDatasetModal
          onClose={() => setShowModal(false)}
          onAdded={() => queryClient.invalidateQueries({ queryKey: ["datasets"] })}
        />
      )}

      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-5 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">ParticleSight</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            AI-powered insight discovery for CERN open data
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowModal(true)}
            className="rounded-lg bg-blue-600 hover:bg-blue-700 px-4 py-2 text-sm font-medium text-white transition-colors"
          >
            + Add Dataset
          </button>
          <a href="/history" className="text-sm text-blue-600 hover:underline">
            View History →
          </a>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800">
            Available Datasets
          </h2>
          <p className="text-gray-500 text-sm mt-1">
            Select a dataset to automatically discover correlations, anomalies,
            and AI-generated insights.
          </p>
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center gap-3 text-gray-500">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Loading datasets...
          </div>
        )}

        {/* Error state */}
        {isError && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
            Could not load datasets. Make sure the backend is running at
            http://localhost:8000
          </div>
        )}

        {/* Dataset grid */}
        {datasets && datasets.length === 0 && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 rounded-lg px-4 py-3 text-sm">
            No datasets found. Add one via{" "}
            <code className="bg-yellow-100 px-1 rounded">
              POST /api/datasets/
            </code>{" "}
            in the API docs.
          </div>
        )}

        {datasets && datasets.length > 0 && (
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
      </main>
    </div>
  );
}
