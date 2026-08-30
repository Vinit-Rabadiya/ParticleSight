import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDatasets } from "../hooks/useDatasets";
import DatasetCard from "../components/DatasetCard";
import client from "../api/client";
import { useQueryClient } from "@tanstack/react-query";

const STEP = { INPUT: "input", LOADING: "loading", PREVIEW: "preview", ADDING: "adding" };

export default function Home() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: datasets, isLoading, isError } = useDatasets();

  // Add dataset inline form state
  const [url, setUrl] = useState("");
  const [step, setStep] = useState(STEP.INPUT);
  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [formError, setFormError] = useState("");

  async function handleAnalyse(datasetId) {
    try {
      const response = await client.post(`/api/analysis/?dataset_id=${datasetId}`);
      navigate(`/dashboard/${response.data.analysis_id}`);
    } catch (err) {
      console.error("Failed to start analysis:", err);
      alert("Could not start analysis. Is the backend running?");
    }
  }

  async function handleFetch() {
    if (!url.trim()) return;
    setFormError("");
    setStep(STEP.LOADING);
    try {
      const res = await client.get("/api/datasets/preview", { params: { cern_url: url.trim() } });
      setPreview(res.data);
      setSelectedFile(res.data.csv_files?.[0] ?? null);
      setStep(STEP.PREVIEW);
    } catch (err) {
      setFormError(err.response?.data?.detail || "Could not fetch that URL. Make sure it's a valid CERN Open Data record link.");
      setStep(STEP.INPUT);
    }
  }

  async function handleAdd() {
    if (!selectedFile) return;
    setStep(STEP.ADDING);
    try {
      await client.post("/api/datasets/", null, {
        params: { cern_record_id: preview.record_id, csv_url: selectedFile.url },
      });
      // Reset form and refresh dataset list
      setUrl("");
      setPreview(null);
      setSelectedFile(null);
      setStep(STEP.INPUT);
      queryClient.invalidateQueries({ queryKey: ["datasets"] });
    } catch (err) {
      setFormError(err.response?.data?.detail || "Failed to add dataset.");
      setStep(STEP.PREVIEW);
    }
  }

  function handleReset() {
    setUrl("");
    setPreview(null);
    setSelectedFile(null);
    setStep(STEP.INPUT);
    setFormError("");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-5 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">ParticleSight</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            AI-powered insight discovery for CERN open data
          </p>
        </div>
        <a href="/history" className="text-sm text-blue-600 hover:underline">
          View History →
        </a>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-10 space-y-10">

        {/* ── Add Dataset section ── */}
        <section className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-1">Add a CERN Dataset</h2>
          <p className="text-sm text-gray-500 mb-4">
            Paste any{" "}
            <a href="https://opendata.cern.ch" target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">
              CERN Open Data
            </a>{" "}
            record URL and we'll fetch the metadata automatically.
          </p>

          {/* URL row */}
          <div className="flex gap-2">
            <input
              type="url"
              value={url}
              onChange={(e) => { setUrl(e.target.value); if (preview) handleReset(); }}
              onKeyDown={(e) => e.key === "Enter" && step === STEP.INPUT && handleFetch()}
              placeholder="https://opendata.cern.ch/record/700"
              disabled={step === STEP.LOADING || step === STEP.ADDING}
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50"
            />
            {step !== STEP.PREVIEW
              ? (
                <button
                  onClick={handleFetch}
                  disabled={!url.trim() || step === STEP.LOADING}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {step === STEP.LOADING ? "Fetching…" : "Fetch"}
                </button>
              ) : (
                <button
                  onClick={handleReset}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  Clear
                </button>
              )
            }
          </div>

          {/* Error */}
          {formError && (
            <p className="mt-2 text-sm text-red-600">{formError}</p>
          )}

          {/* Preview */}
          {step === STEP.PREVIEW && preview && (
            <div className="mt-4 rounded-xl border border-emerald-100 bg-emerald-50 p-4 space-y-3">
              {/* Metadata */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-semibold text-sm text-gray-900">{preview.title}</p>
                  <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-500">
                    {preview.year && <span>{preview.year}</span>}
                    {preview.doi_url && (
                      <a href={preview.doi_url} target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">
                        View on CERN ↗
                      </a>
                    )}
                  </div>
                </div>
                {preview.experiment && (
                  <span className="shrink-0 rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                    {preview.experiment}
                  </span>
                )}
              </div>

              {preview.description && (
                <p className="text-xs text-gray-600 line-clamp-2">{preview.description}</p>
              )}

              {/* File picker + Add button */}
              {preview.csv_files?.length > 0 ? (
                <div className="flex items-center gap-3">
                  <select
                    value={selectedFile?.url ?? ""}
                    onChange={(e) => setSelectedFile(preview.csv_files.find((f) => f.url === e.target.value))}
                    className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                  >
                    {preview.csv_files.map((f) => (
                      <option key={f.url} value={f.url}>
                        {f.name} — {f.size_mb} MB
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={handleAdd}
                    disabled={step === STEP.ADDING}
                    className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
                  >
                    {step === STEP.ADDING ? "Adding…" : "Add Dataset"}
                  </button>
                </div>
              ) : (
                <p className="text-sm text-yellow-700">No CSV files found for this record.</p>
              )}
            </div>
          )}
        </section>

        {/* ── Dataset grid ── */}
        <section>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800">Available Datasets</h2>
            <p className="text-gray-500 text-sm mt-1">
              Select a dataset to automatically discover correlations, anomalies, and AI-generated insights.
            </p>
          </div>

          {isLoading && (
            <div className="flex items-center gap-3 text-gray-500">
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              Loading datasets...
            </div>
          )}

          {isError && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
              Could not load datasets. Make sure the backend is running.
            </div>
          )}

          {datasets && datasets.length === 0 && (
            <div className="bg-gray-50 border border-gray-200 rounded-xl px-6 py-10 text-center text-gray-500 text-sm">
              No datasets yet. Add your first one above.
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
        </section>
      </main>
    </div>
  );
}
