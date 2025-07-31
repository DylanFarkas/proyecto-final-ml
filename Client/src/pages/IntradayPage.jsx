import { useState, useEffect } from "react";
import {
  runIntradayStrategy,
  getAvailableDates,
  getReturns,
  getDailyReturns,
  getDownloadLink,
} from "../api/intradayAPI";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import { Play, Download } from "lucide-react";
import { useAlert } from "../contexts/AlertContext";
import PageWrapper from "../components/common/PageWrapper";

const IntradayPage = () => {
  const [status, setStatus] = useState("");
  const [dates, setDates] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [returnsData, setReturnsData] = useState([]);
  const [tipoRetorno, setTipoRetorno] = useState("acumulado");
  const [loading, setLoading] = useState(false);
  const { showError, showSuccess, showWarning } = useAlert();

  const loadDates = async () => {
    try {
      const res = await getAvailableDates();
      setDates(res);
    } catch (error) {
      showError(error.message || "Error al cargar fechas disponibles");
    }
  };

  const handleRunStrategy = async () => {
    setLoading(true);
    setStatus("Ejecutando estrategia...");

    try {
      const res = await runIntradayStrategy();
      setStatus(res.message);
      await loadDates();
      showSuccess("Estrategia intradía ejecutada con éxito. Seleccione las fechas para ver los resultados.");
    } catch (error) {
      setStatus("❌ Error al ejecutar la estrategia");
      showError(error.message || "Error al ejecutar la estrategia intradía");
    } finally {
      setLoading(false);
    }
  };

  const loadReturns = async () => {
    if (!startDate || !endDate) {
      showWarning("Por favor seleccione fechas de inicio y fin");
      return;
    }

    if (new Date(startDate) > new Date(endDate)) {
      showError("La fecha de inicio debe ser anterior a la fecha de fin");
      return;
    }

    try {
      const fn = tipoRetorno === "diario" ? getDailyReturns : getReturns;
      const data = await fn(startDate, endDate);
      setReturnsData(data);
    } catch (error) {
      showError(error.message || "Error al obtener retornos");
    }
  };

  useEffect(() => {
    loadDates();
  }, []);

  useEffect(() => {
    if (startDate && endDate) {
      loadReturns();
    }
  }, [startDate, endDate, tipoRetorno]);

  return (
    <PageWrapper pageName="Intraday Strategy">
      <div className="max-w-7xl mx-auto p-6 space-y-8">

        {/* Header */}
        <div className="flex justify-between items-center dark:bg-gray-800 p-4 rounded-md shadow">
          <h2 className="text-2xl font-bold text-blue-800 dark:text-white">
            Estrategia Intradía
          </h2>
          <button
            onClick={handleRunStrategy}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 cursor-pointer bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition"
          >
            <Play className="w-4 h-4" />
            {loading ? "Ejecutando..." : "Ejecutar Estrategia"}
          </button>
        </div>

        {status && (
          <p className="text-sm text-gray-600 dark:text-gray-400">{status}</p>
        )}

        {/* Filtros */}
        <div className="bg-white dark:bg-gray-800 rounded shadow p-6 space-y-4">
          <div className="flex flex-wrap gap-4 items-center">
            <label className="text-sm text-gray-700 dark:text-gray-300">Tipo de retorno:</label>
            <select
              value={tipoRetorno}
              onChange={(e) => setTipoRetorno(e.target.value)}
              className="border px-3 py-2 rounded cursor-pointer dark:bg-gray-800 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600"
              disabled={loading}
            >
              <option value="acumulado">Acumulado (%)</option>
              <option value="diario">Diario (%)</option>
            </select>
          </div>

          <div className="flex flex-wrap gap-4 items-center">
            <div>
              <label className="mr-2 text-gray-700 dark:text-gray-300">Inicio:</label>
              <select
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="border px-3 py-2 rounded cursor-pointer dark:bg-gray-800 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600"
                disabled={loading}
              >
                <option value="">Seleccionar fecha de inicio</option>
                {dates.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="mr-2 text-gray-700 dark:text-gray-300">Fin:</label>
              <select
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="border px-3 py-2 rounded cursor-pointer dark:bg-gray-800 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600"
                disabled={loading}
              >
                <option value="">Seleccionar fecha de fin</option>
                {dates.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            
          </div>
        </div>

        {/* Gráfico */}
        <div className="bg-white dark:bg-gray-800 rounded shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Retornos ({tipoRetorno})</h3>

            {startDate && endDate && (
              <a
                href={getDownloadLink(startDate, endDate, tipoRetorno)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                download
              >
                <Download className="w-4 h-4" />
                Descargar CSV
              </a>
            )}
          </div>

          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={returnsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis unit="%" />
              <Tooltip />
              <Legend />
              {tipoRetorno === "diario" ? (
                <Line
                  type="monotone"
                  dataKey="strategy_return"
                  name="Retorno diario (%)"
                  stroke="#AD46FF"
                  dot={false}
                />
              ) : (
                <Line
                  type="monotone"
                  dataKey="cumulative_strategy_return"
                  name="Retorno acumulado (%)"
                  stroke="#155DFC"
                  dot={false}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </PageWrapper>
  );
};

export default IntradayPage;
