import { useState } from "react";
import client from "../api/client";

// Three steps: input → preview → done
const STEP = { INPUT: "input", LOADING: "loading", PREVIEW: "preview", ADDING: "adding" };

export default function AddDatasetModal({ onClose, onAdded }) {
  const [step, setStep] = useState(STEP.INPUT);
  const [url, setUrl] = useState("");
  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");

  async function handlePreview() {
    if (!url.trim()) return;
    setError("");
    setStep(STEP.LOADING);
    try {
      const res = await client.get("/api/datasets/preview", { params: { cern_url: url.trim() } });
      setPreview(res.data);
      setSelectedFile(res.data.csv_files?.[0] ?? null);
      setStep(STEP.PREVIEW);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not fetch that URL. Make sure it's a valid CERN Open Data record link.");
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
      onAdded();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add dataset.");
      setStep(STEP.PREVIEW);
    }
  }

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="w-full max-w-lg rounded-2xl bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <h2 className="text-base font-semibold text-gray-900">Add a CERN Dataset</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>

        <div className="px-6 py-5 space-y-4">
          {/* URL input — always visible */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              CERN Open Data record URL
            </label>
            <div className="flex gap-2">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && step === STEP.INPUT && handlePreview()}
                placeholder="https://opendata.cern.ch/record/700"
                className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                disabled={step === STEP.LOADING || step === STEP.ADDING}
              />
              {step !== STEP.PREVIEW && (
                <button
                  onClick={handlePreview}
                  disabled={!url.trim() || step === STEP.LOADING}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {step === STEP.LOADING ? "Fetching..." : "Fetch"}
                </button>
              )}
              {step === STEP.PREVIEW && (
                <button
                  onClick={() => { setStep(STEP.INPUT); setPreview(null); setError(""); }}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  Change
                </button>
              )}
            </div>
            <p className="mt-1 text-xs text-gray-400">
              e.g. https://opendata.cern.ch/record/700
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Preview */}
          {step === STEP.PREVIEW && preview && (
            <div className="space-y-4">
              {/* Metadata card */}
              <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-4 space-y-1">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-sm font-semibold text-gray-900 leading-snug">{preview.title}</h3>
                  {preview.experiment && (
                    <span className="shrink-0 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">
                      {preview.experiment}
                    </span>
                  )}
                </div>
                <div className="flex gap-3 text-xs text-gray-500">
                  {preview.year && <span>{preview.year}</span>}
                  {preview.doi_url && (
                    <a href={preview.doi_url} target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">
                      View on CERN ↗
                    </a>
                  )}
                </div>
                {preview.description && (
                  <p className="text-xs text-gray-600 line-clamp-2 mt-1">{preview.description}</p>
                )}
              </div>

              {/* File picker */}
              {preview.csv_files?.length > 0 ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Select CSV file
                    <span className="ml-1 text-xs font-normal text-gray-400">({preview.csv_files.length} available)</span>
                  </label>
                  <select
                    value={selectedFile?.url ?? ""}
                    onChange={(e) => setSelectedFile(preview.csv_files.find((f) => f.url === e.target.value))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    {preview.csv_files.map((f) => (
                      <option key={f.url} value={f.url}>
                        {f.name} ({f.size_mb} MB)
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <div className="rounded-lg bg-yellow-50 border border-yellow-200 px-4 py-3 text-sm text-yellow-700">
                  No CSV files found for this record.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 border-t border-gray-100 px-6 py-4">
          <button
            onClick={onClose}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          {step === STEP.PREVIEW && (
            <button
              onClick={handleAdd}
              disabled={!selectedFile || step === STEP.ADDING}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {step === STEP.ADDING ? "Adding..." : "Add Dataset"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
