import React, { useState, useEffect } from 'react';
import { getComparisonData, getDownloadSentimentProgress } from '../api/sentimentAPI';
import { getComparisonIntradayData, getDownloadProgress as getIntradailyDownloadProgress } from '../api/intradayAPI';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Swal from 'sweetalert2';
import PageWrapper from '../components/common/PageWrapper';
import { PlayCircle, RefreshCw, AlertTriangle, BarChart3 } from 'lucide-react';

const BenchMarkingPage = () => {
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [selectedApp, setSelectedApp] = useState("sentiment");

  const fetchComparisonData = async () => {
    setLoading(true);
    setError(null);
    try {
      let data;
      const localData = localStorage.getItem(`comparisonData_${selectedApp}`);
      if (localData) {
        setComparisonData(JSON.parse(localData));
        setLoading(false);
        return;
      }
      data = selectedApp === "sentiment" ? await getComparisonData() : await getComparisonIntradayData();
      localStorage.setItem(`comparisonData_${selectedApp}`, JSON.stringify(data));
      setComparisonData(data);
      Swal.fire({ title: "¡Datos obtenidos correctamente!", text: "La comparación de rendimiento se ha cargado con éxito", icon: "success", confirmButtonText: "Aceptar", confirmButtonColor: "#2563eb" });
    } catch (error) {
      setError(error.message || 'Hubo un error al obtener los datos.');
      let errorTitle = "Error", errorIcon = "error", errorText = error.message;
      if (error.message?.includes('Timeout') || error.message?.includes('⏱️')) {
        errorTitle = "Operación Lenta"; errorIcon = "warning";
      } else if (error.message?.includes('Archivo no encontrado') || error.message?.includes('📁')) {
        errorTitle = "Archivos No Encontrados"; errorIcon = "info";
      } else if (error.message?.includes('Error de conexión') || error.message?.includes('🌐')) {
        errorTitle = "Problema de Conexión"; errorIcon = "error";
      }
      Swal.fire({ title: errorTitle, text: errorText, icon: errorIcon, confirmButtonText: "Aceptar", confirmButtonColor: "#dc2626", footer: selectedApp === "sentiment" ? '<small>Asegúrese de que el archivo sentiment_data.csv esté disponible</small>' : '<small>Asegúrese de que los archivos de datos intradía estén disponibles</small>' });
    } finally {
      setLoading(false);
    }
  };

  const fetchDownloadProgress = async () => {
    try {
      const response = selectedApp === "sentiment" ? await getDownloadSentimentProgress() : await getIntradailyDownloadProgress();
      setDownloadProgress(response.progress);
    } catch (error) {
      console.error('Error obteniendo el progreso de descarga:', error);
    }
  };

  useEffect(() => {
    if (loading) {
      const interval = setInterval(fetchDownloadProgress, 1000);
      return () => clearInterval(interval);
    }
  }, [loading]);

  const handleRecalculate = () => {
    localStorage.removeItem(`comparisonData_${selectedApp}`);
    fetchComparisonData();
  };

  const chartData = comparisonData ? [
    { name: 'Secuencial', tiempo: comparisonData.secuencial.tiempo, cpu: comparisonData.secuencial.cpu },
    { name: 'Paralelo', tiempo: comparisonData.paralelo.tiempo, cpu: comparisonData.paralelo.cpu },
  ] : [];

  return (
    <PageWrapper pageName="Benchmarking">
      <div className="p-6 bg-white dark:bg-gray-800 rounded-md shadow-md space-y-6">
        <div className="flex justify-between items-center bg-blue-100 dark:bg-blue-900 p-4 rounded-md shadow">
          <div>
            <h1 className="text-2xl font-bold text-blue-800 dark:text-white flex items-center gap-2">
              <BarChart3 className="w-6 h-6" /> Benchmarking de Estrategias
            </h1>
            <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
              Compara el rendimiento entre ejecución secuencial y paralela.
            </p>
          </div>
          <select
            value={selectedApp}
            onChange={(e) => setSelectedApp(e.target.value)}
            className="border border-gray-300 bg-gray-300 dark:border-gray-700 rounded px-4 py-2 text-sm dark:bg-gray-800 text-gray-800 dark:text-white"
          >
            <option value="sentiment">Análisis de sentimiento</option>
            <option value="intradaily">Estrategia Intradía</option>
          </select>
        </div>

        <div className="flex flex-wrap gap-4">
          <button
            onClick={fetchComparisonData}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition"
          >
            <PlayCircle className="w-5 h-5" /> {loading ? 'Cargando...' : 'Obtener Datos'}
          </button>

          <button
            onClick={handleRecalculate}
            disabled={loading}
            className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:opacity-50 transition"
          >
            <RefreshCw className="w-5 h-5" /> Recalcular
          </button>
        </div>

        {loading && (
          <>
            <div className="bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 dark:border-yellow-700 rounded-md p-4 flex items-start gap-3">
              <AlertTriangle className="text-yellow-600 dark:text-yellow-300 w-6 h-6 mt-1" />
              <div>
                <h3 className="font-semibold text-yellow-800 dark:text-yellow-200">La operación puede tardar varios minutos</h3>
                <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1 leading-relaxed">
                  • Se ejecutan ambos pipelines: secuencial y paralelo.<br />
                  • Puede tomar hasta 3 minutos.<br />
                  • Se le notificará automáticamente al finalizar.
                </p>
              </div>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mt-4">
              <div className="bg-blue-600 h-3 rounded-full transition-all duration-500" style={{ width: `${downloadProgress}%` }} />
            </div>
            <p className="text-sm mt-1 text-gray-700 dark:text-gray-300">
              Progreso: <strong>{downloadProgress}%</strong> {downloadProgress < 50 ? '(Ejecutando versión secuencial...)' : '(Ejecutando versión paralela...)'}
            </p>
          </>
        )}

        {comparisonData && (
          <div className="space-y-6">
            <table className="min-w-full text-sm text-left bg-white dark:bg-gray-700 rounded-md overflow-hidden shadow">
              <thead className="bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-white">
                <tr>
                  <th className="px-4 py-3">Método</th>
                  <th className="px-4 py-3">Tiempo (segundos)</th>
                  <th className="px-4 py-3">Uso de CPU (%)</th>
                </tr>
              </thead>
              <tbody>
                {["secuencial", "paralelo"].map((tipo, i) => (
                  <tr key={tipo} className={i % 2 === 0 ? "bg-white dark:bg-gray-700" : "bg-gray-50 dark:bg-gray-800"}>
                    <td className="px-4 py-2 text-gray-800 dark:text-white capitalize">{tipo}</td>
                    <td className="px-4 py-2 text-gray-800 dark:text-white">{comparisonData[tipo].tiempo}</td>
                    <td className="px-4 py-2 text-gray-800 dark:text-white">{comparisonData[tipo].cpu}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="bg-white dark:bg-gray-800 rounded-md shadow p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Comparación Gráfica: Secuencial vs Paralelo
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="tiempo" fill="#2B7FFF" barSize={30} />
                  <Bar dataKey="cpu" fill="#AD46FF" barSize={30} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </PageWrapper>
  );
};

export default BenchMarkingPage;