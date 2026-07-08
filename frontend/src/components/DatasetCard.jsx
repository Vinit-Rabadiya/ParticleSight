function DatasetCard({ dataset, onAnalyse }) {
  const badgeClass =
    dataset.experiment === "CMS"
      ? "bg-blue-100 text-blue-800"
      : "bg-orange-100 text-orange-800";

  return (
    <div className="bg-white rounded-xl shadow p-6 flex flex-col gap-4 border border-gray-100">
      <h2 className="text-xl font-bold">{dataset.name}</h2>

      <span
        className={`inline-block px-3 py-1 rounded-full text-sm font-medium w-fit ${badgeClass}`}
      >
        {dataset.experiment}
      </span>

      <p>
        <strong>Year:</strong> {dataset.year}
      </p>

      <p>{dataset.description}</p>

      {dataset.doi_url && (
        <a
          href={dataset.doi_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          View on CERN
        </a>
      )}

      <button
        onClick={() => onAnalyse(dataset.id)}
        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
      >
        Analyse This Dataset
      </button>
    </div>
  );
}

export default DatasetCard;