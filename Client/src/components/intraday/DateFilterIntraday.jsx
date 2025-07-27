const DateFilterIntraday = ({
  startDate,
  endDate,
  setStartDate,
  setEndDate,
  onFilter,
  onDownload,
  availableDates = [],
}) => {
  return (
    <div className="flex flex-wrap items-center gap-4 mb-4">
      <div>
        <label className="mr-2">Inicio:</label>
        <select
          value={startDate}
          onChange={e => setStartDate(e.target.value)}
          className="border px-2 py-1 rounded"
        >
          <option value="">Seleccionar fecha</option>
          {availableDates.map((date) => (
            <option key={date} value={date}>
              {date}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="mr-2">Fin:</label>
        <select
          value={endDate}
          onChange={e => setEndDate(e.target.value)}
          className="border px-2 py-1 rounded"
        >
          <option value="">Seleccionar fecha</option>
          {availableDates.map((date) => (
            <option key={date} value={date}>
              {date}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={onFilter}
        className="bg-blue-500 text-white px-4 py-1 rounded hover:bg-blue-600"
      >
        Filtrar
      </button>

      <button
        onClick={onDownload}
        className="bg-green-500 text-white px-4 py-1 rounded hover:bg-green-600"
      >
        Descargar CSV
      </button>
    </div>
  );
};

export default DateFilterIntraday;
