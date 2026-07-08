function CorrelationMatrix({ correlations }) {
  return (
    <div className="rounded-lg border bg-white p-4 shadow">
      <h1 className="text-lg font-semibold">Top Correlations</h1>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            <th className="border border-gray-200 px-3 py-2 text-left">
              Variable 1
            </th>
            <th className="border border-gray-200 px-3 py-2 text-left">
              Variable 2
            </th>
            <th className="border border-gray-200 px-3 py-2 text-left">
              r value
            </th>
            <th className="border border-gray-200 px-3 py-2 text-left">
              Strength
            </th>
            <th className="border border-gray-200 px-3 py-2 text-left">
              Direction
            </th>
          </tr>
        </thead>
        <tbody>
          {correlations.map((correlation, i) => {
            const absCorrelation = Math.abs(correlation.correlation);

            let correlationColor = "bg-gray-100";

            if (absCorrelation > 0.7) {
              correlationColor = "bg-green-100";
            } else if (absCorrelation > 0.4) {
              correlationColor = "bg-yellow-100";
            }

            return (
              <tr key={i}>
                <td className="border border-gray-200 px-3 py-2">
                  {correlation.variable_1}
                </td>

                <td className="border border-gray-200 px-3 py-2">
                  {correlation.variable_2}
                </td>

                <td
                  className={`border border-gray-200 px-3 py-2 ${correlationColor}`}
                >
                  {correlation.correlation.toFixed(2)}
                </td>

                <td className="border border-gray-200 px-3 py-2">
                  <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800">
                    {correlation.strength}
                  </span>
                </td>

                <td className="border border-gray-200 px-3 py-2">
                  {correlation.direction}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default CorrelationMatrix;
