const FilteredReturnsTable = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <div className="overflow-x-auto mt-4">
      <table className="min-w-full text-sm text-left text-gray-800 dark:text-gray-100">
        <thead className="bg-blue-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 uppercase text-xs">
          <tr>
            <th className="px-4 py-2">Fecha</th>
            <th className="px-4 py-2">Portafolio</th>
            <th className="px-4 py-2">Nasdaq</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr
              key={idx}
              className={
                idx % 2 === 0
                  ? "bg-white dark:bg-gray-800"
                  : "bg-gray-50 dark:bg-gray-700"
              }
            >
              <td className="px-4 py-2">{row.Date}</td>
              <td className="px-4 py-2">{row.portfolio_returns.toFixed(4)}</td>
              <td className="px-4 py-2">{row.nasdaq_return.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FilteredReturnsTable;