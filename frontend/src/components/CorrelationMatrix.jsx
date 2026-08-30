// Shows a table of top correlations between column pairs
// Props: correlations (array from API)
export default function CorrelationMatrix({ correlations }) {
  // Returns Tailwind background colour based on correlation strength and direction
  function getCellColour(r) {
    const abs = Math.abs(r);
    if (abs > 0.7) return r > 0 ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800";
    if (abs > 0.4) return "bg-yellow-100 text-yellow-800";
    return "bg-gray-100 text-gray-600";
  }

  function getStrengthBadge(strength) {
    const colours = {
      strong: "bg-green-100 text-green-700",
      moderate: "bg-yellow-100 text-yellow-700",
      weak: "bg-gray-100 text-gray-500",
    };
    return colours[strength] || "bg-gray-100 text-gray-500";
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="text-base font-semibold text-gray-800 mb-4">
        Top Correlations
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left px-3 py-2 text-gray-500 font-medium">Variable 1</th>
              <th className="text-left px-3 py-2 text-gray-500 font-medium">Variable 2</th>
              <th className="text-left px-3 py-2 text-gray-500 font-medium">r value</th>
              <th className="text-left px-3 py-2 text-gray-500 font-medium">Strength</th>
              <th className="text-left px-3 py-2 text-gray-500 font-medium">Direction</th>
            </tr>
          </thead>
          <tbody>
            {correlations.map((c, i) => (
              <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-3 py-2 font-mono text-gray-700">{c.variable_1}</td>
                <td className="px-3 py-2 font-mono text-gray-700">{c.variable_2}</td>
                <td className="px-3 py-2">
                  <span className={`px-2 py-0.5 rounded font-mono text-xs font-semibold ${getCellColour(c.correlation)}`}>
                    {c.correlation.toFixed(3)}
                  </span>
                </td>
                <td className="px-3 py-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStrengthBadge(c.strength)}`}>
                    {c.strength}
                  </span>
                </td>
                <td className="px-3 py-2 text-gray-500 capitalize">{c.direction}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
