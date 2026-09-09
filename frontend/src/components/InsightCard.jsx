function InsightCard({ insight }) {
  const { title, explanation, surprise_level, finding_type } = insight;

  const badgeColors = {
    correlation: "bg-blue-100 text-blue-800",
    anomaly: "bg-red-100 text-red-800",
    distribution: "bg-purple-100 text-purple-800",
    pattern: "bg-green-100 text-green-800",
  };

  let surpriseColor = "bg-green-500";
  if (surprise_level >= 7) {
    surpriseColor = "bg-red-500";
  } else if (surprise_level >= 4) {
    surpriseColor = "bg-yellow-500";
  }

  // The backend sometimes returns explanation as a newline-separated bullet
  // list (each line starting with "-"), e.g. the "Column Meanings" insight.
  // Render those as a proper <ul> instead of collapsing them into one
  // run-on paragraph, which is what plain HTML whitespace handling does.
  const lines = (explanation || "").split("\n").map((l) => l.trim()).filter(Boolean);
  const isBulletList = lines.length > 1 && lines.every((l) => l.startsWith("-"));

  return (
    <div className="bg-white rounded-xl shadow p-5 border border-gray-100 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-lg">{title}</h3>

        <span
          className={`rounded-full px-2 py-1 text-xs font-medium ${
            badgeColors[finding_type] || "bg-gray-100 text-gray-700"
          }`}
        >
          {finding_type}
        </span>
      </div>

      {isBulletList ? (
        <ul className="text-gray-700 list-disc pl-5 flex flex-col gap-1.5">
          {lines.map((line, i) => (
            <li key={i}>{line.replace(/^-\s*/, "")}</li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-700 whitespace-pre-line">{explanation}</p>
      )}

      <div className="flex flex-col gap-2">
        <span className="text-sm font-medium">
          Surprise: {surprise_level}/10
        </span>

        <div className="flex gap-1">
          {Array.from({ length: 10 }, (_, i) => (
            <div
              key={i}
              className={`h-3 w-3 rounded-full ${
                i < surprise_level ? surpriseColor : "bg-gray-200"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default InsightCard;
