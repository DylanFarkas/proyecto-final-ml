import { useEffect, useState } from "react";
import { getStats } from "../../api/sentimentAPI";
import { useRetryableRequest } from "../../hooks/useRetryableRequest";

const StatsSummary = () => {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(false);
  const { loading, executeRequest } = useRetryableRequest(2, 2000);

  useEffect(() => {
    let isMounted = true;
    
    const fetchStats = async () => {
      try {
        await executeRequest(
          () => getStats(),
          {
            onSuccess: (data) => {
              if (isMounted) {
                setStats(data.data);
                setError(false);
              }
            },
            onError: () => {
              if (isMounted) {
                setError(true);
              }
            },
            retryOnError: false // No retry automatico para evitar loops
          }
        );
      } catch (error) {
        // Error ya manejado por useRetryableRequest
        if (isMounted) {
          setError(true);
        }
      }
    };

    fetchStats();
    
    return () => {
      isMounted = false;
    };
  }, []); // Sin dependencias para evitar loops

  if (loading) return <p className="text-gray-500 dark:text-gray-400">Cargando estadísticas...</p>;
  if (error && !stats) return (
    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p className="text-red-700 dark:text-red-300">Error al cargar estadísticas</p>
    </div>
  );
  if (!stats) return null;

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