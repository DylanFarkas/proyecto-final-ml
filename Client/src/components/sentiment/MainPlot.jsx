import { useEffect, useState } from "react";
import { getSentimentReturns } from "../../api/sentimentAPI";
import { useAlert } from "../../contexts/AlertContext";
import InteractivePlot from "./InteractivePlot";

const MainPlot = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const { showError } = useAlert();

  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(false);
        const res = await getSentimentReturns();
        
        if (isMounted) {
          setData(res.data);
        }
      } catch (error) {
        if (isMounted) {
          setError(true);
          showError(error.message || "Error al cargar el gráfico principal");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();
    
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg">
        <p className="text-gray-500 dark:text-gray-400">Cargando gráfico...</p>
      </div>
    );
  }

  if (error && data.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <p className="text-red-700 dark:text-red-300">Error al cargar el gráfico</p>
      </div>
    );
  }

  return <InteractivePlot data={data} />;
};

export default MainPlot;
