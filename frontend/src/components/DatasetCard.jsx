// Displays one CERN dataset as a card with an Analyse button
// Props: dataset (object from API), onAnalyse (function called with dataset.id)

export default function DatasetCard({ dataset, onAnalyse }) {
  // Colour the experiment badge differently per experiment
  const experimentColours = {
    CMS: "bg-blue-100 text-blue-800",
    ATLAS: "bg-orange-100 text-orange-800",
    ALICE: "bg-green-100 text-green-800",
    LHCb: "bg-purple-100 text-purple-800",
  };
  const badgeColour =
    experimentColours[dataset.experiment] || "bg-gray-100 text-gray-700";

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col gap-4 hover:shadow-md transition-shadow">
      {/* Name + experiment badge */}
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-base font-semibold text-gray-900 leading-snug">
          {dataset.name}
        </h3>
        {dataset.experiment && (
          <span
            className={`text-xs font-medium px-2 py-1 rounded-full shrink-0 ${badgeColour}`}
          >
            {dataset.experiment}
          </span>
        )}
      </div>

      {/* Year + DOI link */}
      <div className="flex items-center gap-4 text-sm text-gray-500">
        {dataset.year && <span>{dataset.year}</span>}
        {dataset.doi_url && (
          <a
            href={dataset.doi_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
            View on CERN ↗
          </a>
        )}
      </div>

      {/* Description */}
      {dataset.description && (
        <p className="text-sm text-gray-600 line-clamp-3">
          {dataset.description}
        </p>
      )}

      {/* Analyse button */}
      <button
        onClick={() => onAnalyse(dataset.id)}
        className="mt-auto w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-sm font-medium py-2.5 rounded-lg transition-colors"
      >
        Analyse This Dataset
      </button>
    </div>
  );
}
