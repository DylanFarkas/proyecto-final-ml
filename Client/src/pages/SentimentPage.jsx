import StatsSummary from "../components/sentiment/StatsSummary";
import FilteredReturns from "../components/sentiment/FilteredReturns";
import InteractivePlot from "../components/sentiment/InteractivePlot";

const SentimentPage = () => {
  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <h2 className="text-3xl font-bold text-blue-800 mt-4 dark:text-white">Análisis de Sentimiento Financiero</h2>

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
