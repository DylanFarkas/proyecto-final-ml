import { useEffect, useState, useCallback } from "react";
import { getAvailableDates, getFilteredReturns, downloadFilteredReturnsCSV } from "../../api/sentimentAPI";
import InteractivePlot from "./InteractivePlot";
import DateFilter from "./DateFilter";
import FilteredReturnsTable from "./FilteredReturnsTable";
import { useAlert } from "../../contexts/AlertContext";

const FilteredReturns = () => {
  const [dates, setDates] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const { showError, showSuccess } = useAlert();

  useEffect(() => {
    let isMounted = true;
    
    const initializeData = async () => {
      if (initialized) return; // Prevenir múltiples inicializaciones
      
      try {
        setLoading(true);
        const res = await getAvailableDates();
        
        if (!isMounted) return;
        
        const availableDates = res.data.dates;
        setDates(availableDates);
        
        if (availableDates.length > 0) {
          const firstDate = availableDates[0];
          const lastDate = availableDates[availableDates.length - 1];
          setStartDate(firstDate);
          setEndDate(lastDate);

          const filteredRes = await getFilteredReturns(firstDate, lastDate);
          if (isMounted) {
            setFilteredData(filteredRes.data);
            setInitialized(true);
          }
        }
      } catch (error) {
        if (isMounted) {
          showError(error.message || "Error al cargar datos iniciales");
          setInitialized(true); // Marcar como inicializado para evitar reintentos
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    initializeData();
    
    return () => {
      isMounted = false;
    };
  }, []); // Sin dependencias para evitar ciclos

  const handleFilter = useCallback(async () => {
    if (!startDate || !endDate) {
      showError("Por favor seleccione fechas de inicio y fin");
      return;
    }

    if (new Date(startDate) > new Date(endDate)) {
      showError("La fecha de inicio debe ser anterior a la fecha de fin");
      return;
    }

    try {
      setLoading(true);
      const res = await getFilteredReturns(startDate, endDate);
      setFilteredData(res.data);
    } catch (error) {
      showError(error.message || "Error al filtrar datos");
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, showError]);

  const handleExport = useCallback(async () => {
    if (!startDate || !endDate) {
      showError("Por favor seleccione fechas de inicio y fin");
      return;
    }

    try {
      setLoading(true);
      await downloadFilteredReturnsCSV(startDate, endDate);
      showSuccess("Archivo CSV descargado con éxito");
    } catch (error) {
      showError(error.message || "Error al descargar archivo");
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, showError, showSuccess]);

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
        loading={loading}
      />

      <InteractivePlot data={filteredData} />

      <div className="flex justify-start">
        <button
          onClick={handleExport}
          disabled={loading || !startDate || !endDate}
          className="bg-blue-600 text-white px-4 py-2 rounded cursor-pointer hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Exportando..." : "Exportar CSV"}
        </button>
      </div>

      <FilteredReturnsTable data={filteredData} />
    </div>
  );
};

export default FilteredReturns;
