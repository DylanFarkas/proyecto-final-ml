const DateFilter = ({ dates, startDate, endDate, onStartChange, onEndChange, onFilter, loading = false }) => {
  return (
    <div className="flex flex-col sm:flex-row gap-4 mb-4">
      <div className="flex flex-col">
        <label className="text-sm mb-1 text-gray-800 dark:text-gray-200">Fecha de inicio</label>
        <select
          className="p-2 border rounded bg-white cursor-pointer dark:bg-gray-800 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600 disabled:opacity-50"
          value={startDate}
          onChange={onStartChange}
          disabled={loading}
        >
          {dates.map((date) => (
            <option key={date} value={date}>{date}</option>
          ))}
        </select>
      </div>

      <div className="flex flex-col">
        <label className="text-sm mb-1 text-gray-800 dark:text-gray-200">Fecha de fin</label>
        <select
          className="p-2 border rounded bg-white cursor-pointer dark:bg-gray-800 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600 disabled:opacity-50"
          value={endDate}
          onChange={onEndChange}
          disabled={loading}
        >
          {dates.map((date) => (
            <option key={date} value={date}>{date}</option>
          ))}
        </select>
      </div>

      <button
        onClick={onFilter}
        disabled={loading || !startDate || !endDate}
        className="self-end bg-blue-600 text-white cursor-pointer px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? "Filtrando..." : "Aplicar filtro"}
      </button>
    </div>
  );
};

export default DateFilter;
