import { useEffect, useState } from "react";
import StatsSummary from "../components/sentiment/StatsSummary";
import FilteredReturns from "../components/sentiment/FilteredReturns";
import InteractivePlot from "../components/sentiment/InteractivePlot";
import RecalculateForm from "../components/sentiment/RecalculateForm";

const SentimentPage = () => {
  const [criterioActivo, setCriterioActivo] = useState(() => {
    return localStorage.getItem("criterioActivo") || "engagement_ratio";
  });

  useEffect(() => {
    localStorage.setItem("criterioActivo", criterioActivo);
  }, [criterioActivo]);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <h2 className="text-3xl font-bold text-blue-800 mt-4 dark:text-white">
        Análisis de Sentimiento Financiero
      </h2>

      <h3 className="text-xl font-medium text-gray-600 dark:text-gray-300">
        Criterio actual: <span className="text-black dark:text-white font-semibold">{criterioActivo}</span>
      </h3>

      <RecalculateForm
        onSuccess={() => { }}
        onCriterioChange={(nuevoCriterio) => setCriterioActivo(nuevoCriterio)}
      />

      <StatsSummary />
      <div>
        <h3 className="text-xl font-semibold mb-2">Gráfico de Retornos Acumulados</h3>
        <InteractivePlot />
      </div>

      <FilteredReturns />
    </div>
  );
};

export default SentimentPage;
