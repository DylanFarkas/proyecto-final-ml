import { useEffect, useState } from "react";
import { getStats } from "../../api/sentimentAPI";

const StatsSummary = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getStats()
      .then((res) => setStats(res.data))
      .catch((err) => console.error("Error al obtener estadísticas:", err));
  }, []);

  if (!stats) return <p className="text-gray-500 dark:text-gray-400">Cargando estadísticas...</p>;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md mt-4">
      <div>
        <h3 className="font-semibold text-blue-700 dark:text-blue-300 mb-1">Portafolio</h3>
        <p className="text-gray-700 dark:text-gray-100">
          Media: <span className="font-mono">{stats.portfolio_mean.toFixed(4)}</span>
        </p>
        <p className="text-gray-700 dark:text-gray-100">
          Desviación estándar: <span className="font-mono">{stats.portfolio_std.toFixed(4)}</span>
        </p>
      </div>

      <div>
        <h3 className="font-semibold text-blue-700 dark:text-blue-300 mb-1">Nasdaq</h3>
        <p className="text-gray-700 dark:text-gray-100">
          Media: <span className="font-mono">{stats.nasdaq_mean.toFixed(4)}</span>
        </p>
        <p className="text-gray-700 dark:text-gray-100">
          Desviación estándar: <span className="font-mono">{stats.nasdaq_std.toFixed(4)}</span>
        </p>
      </div>
    </div>
  );
}

export default StatsSummary;