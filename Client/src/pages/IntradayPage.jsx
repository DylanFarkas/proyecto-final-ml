import React, { useEffect, useState } from 'react';
import {
  getIntradayReturns,
  getIntradayDates,
  getFilteredIntradayReturns,
  getIntradayPlot,
  downloadIntradayCSV
} from '../api/intradayAPI';
import DateFilter from '../components/intraday/DateFilterIntraday';
import ReturnsPlot from '../components/intraday/ReturnsPlotIntraday';
import ReturnsTable from '../components/intraday/ReturnsTableIntraday';
import toast from 'react-hot-toast';

const IntradayPage = () => {
  const [returns, setReturns] = useState([]);
  const [dates, setDates] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [plotUrl, setPlotUrl] = useState(null);

  useEffect(() => {
    // Cargar fechas y setear rangos por defecto
    getIntradayDates().then(res => {
      const fechas = res.data.available_dates;
      setDates(fechas);
      if (fechas.length > 0) {
        setStartDate(fechas[0]);
        setEndDate(fechas[fechas.length - 1]);
        // También cargar retornos iniciales con ese rango
        getFilteredIntradayReturns(fechas[0], fechas[fechas.length - 1])
          .then(res => setReturns(res.data));
      }
    });

    // Cargar gráfico
    getIntradayPlot().then(res => setPlotUrl(URL.createObjectURL(res.data)));
  }, []);

  const handleFilter = () => {
    if (!startDate || !endDate) return toast.error("Fechas inválidas");
    getFilteredIntradayReturns(startDate, endDate)
      .then(res => setReturns(res.data))
      .catch(() => toast.error("Error al filtrar retornos"));
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Estrategia Intradía</h2>

      <DateFilter
        startDate={startDate}
        endDate={endDate}
        setStartDate={setStartDate}
        setEndDate={setEndDate}
        onFilter={handleFilter}
        onDownload={() => downloadIntradayCSV(startDate, endDate)}
        availableDates={dates}
      />

      {plotUrl && <ReturnsPlot plotUrl={plotUrl} />}

      {returns.length > 0 && <ReturnsTable data={returns} />}
    </div>
  );
};

export default IntradayPage;
