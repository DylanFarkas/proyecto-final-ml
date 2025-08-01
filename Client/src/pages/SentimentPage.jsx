import { useEffect, useState } from "react";
import StatsSummary from "../components/sentiment/StatsSummary";
import FilteredReturns from "../components/sentiment/FilteredReturns";
import MainPlot from "../components/sentiment/MainPlot";
import RecalculateForm from "../components/sentiment/RecalculateForm";
import PageWrapper from "../components/common/PageWrapper";

const SentimentPage = () => {
  const [criterioActivo, setCriterioActivo] = useState(() => {
    return localStorage.getItem("criterioActivo") || "engagement_ratio";
  });

  useEffect(() => {
    localStorage.setItem("criterioActivo", criterioActivo);
  }, [criterioActivo]);

  return (
    <PageWrapper pageName="Sentiment Analysis">
      <div className="space-y-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center dark:bg-gray-800 p-4 rounded-md shadow">
          <h2 className="text-3xl font-bold text-blue-800 mt-4 dark:text-white">
            Análisis de Sentimiento Financiero
          </h2>

          <h3 className="text-xl font-medium text-gray-600 dark:text-gray-300">
            Criterio actual: <span className="text-black dark:text-white font-semibold">{criterioActivo}</span>
          </h3>

        </div>

        <RecalculateForm
          onSuccess={() => { }}
          onCriterioChange={(nuevoCriterio) => setCriterioActivo(nuevoCriterio)}
        />

        <StatsSummary />

        <FilteredReturns />
      </div>
    </PageWrapper>
  );
};

export default SentimentPage;
