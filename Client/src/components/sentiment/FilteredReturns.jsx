import { useEffect, useState } from "react";
import { getAvailableDates, getFilteredReturns, downloadFilteredReturnsCSV } from "../../api/sentimentAPI";
import InteractivePlot from "./InteractivePlot";
import DateFilter from "./DateFilter";
import FilteredReturnsTable from "./FilteredReturnsTable";
import toast from "react-hot-toast";

const FilteredReturns = () => {
  const [dates, setDates] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [filteredData, setFilteredData] = useState([]);

  useEffect(() => {
    getAvailableDates()
      .then((res) => {
        setDates(res.data.dates);
        setStartDate(res.data.dates[0]);
        setEndDate(res.data.dates[res.data.dates.length - 1]);

        return getFilteredReturns(res.data.dates[0], res.data.dates[res.data.dates.length - 1]);
      })
      .then((res) => setFilteredData(res.data))
      .catch((err) => console.error("Error inicial:", err));
  }, []);

  const handleFilter = async () => {
    try {
      const res = await getFilteredReturns(startDate, endDate);
      setFilteredData(res.data);
    } catch (err) {
      console.error("Error filtrando retornos:", err);
    }
  };

  const handleExport = () => {
    toast.success("Exportado con éxito");
    downloadFilteredReturnsCSV(startDate, endDate);
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md mt-6 space-y-6">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Filtrar Retornos</h3>

      <DateFilter
        dates={dates}
        startDate={startDate}
        endDate={endDate}
        onStartChange={(e) => setStartDate(e.target.value)}
        onEndChange={(e) => setEndDate(e.target.value)}
        onFilter={handleFilter}
      />

      <InteractivePlot data={filteredData} />

      <div className="flex justify-start">
        <button
          onClick={handleExport}
          className="bg-green-600 text-white px-4 py-2 rounded cursor-pointer hover:bg-green-700 transition"
        >
          Exportar CSV
        </button>
      </div>

      <FilteredReturnsTable data={filteredData} />
    </div>
  );
};

export default FilteredReturns;
