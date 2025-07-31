import PageWrapper from "../components/common/PageWrapper";
import {
  Target,
  Compass,
  MessageCircle,
  BarChart3,
  Settings,
  Lightbulb,
} from "lucide-react";

const Guide = () => {
  return (
    <PageWrapper pageName="Guía de Usuario">
      <div className="p-6 bg-white dark:bg-gray-800 rounded-md shadow-md space-y-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Guía de Usuario</h1>

        <section>
          <h2 className="flex items-center gap-2 text-xl font-semibold text-blue-700 dark:text-blue-400 mb-2">
            <Target className="w-6 h-6" /> Introducción
          </h2>
          <p className="text-gray-700 dark:text-gray-300">
            Esta aplicación es el resultado del Proyecto Final del curso de Infraestructuras Paralelas y Distribuidas.
            Permite ejecutar estrategias financieras con procesamiento paralelo y visualizar su rendimiento en tiempo real.
          </p>
        </section>

        <section>
          <h2 className="flex items-center gap-2 text-xl font-semibold text-blue-700 dark:text-blue-400 mb-2">
            <Compass className="w-6 h-6" /> Navegación
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-2">
            Usa el menú superior para acceder a las diferentes secciones:
          </p>
          <ul className="list-disc list-inside text-gray-700 dark:text-gray-300">
            <li><strong>Guía</strong>: Esta sección.</li>
            <li><strong>Sentiment</strong>: Estrategia mensual basada en análisis de sentimiento en Twitter.</li>
            <li><strong>Intraday</strong>: Estrategia de trading intradía con señales técnicas y GARCH.</li>
            <li><strong>Benchmarking</strong>: Comparación de rendimiento entre ejecución secuencial y paralela.</li>
          </ul>
        </section>

        <section>
          <h2 className="flex items-center gap-2 text-xl font-semibold text-blue-700 dark:text-blue-400 mb-2">
            <MessageCircle className="w-6 h-6" /> Módulo Sentiment
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-2">
            Analiza el engagement de tweets sobre acciones financieras para seleccionar las más destacadas cada mes.
          </p>
          <ul className="list-disc list-inside text-gray-700 dark:text-gray-300">
            <li>Haz clic en <strong>"Recalcular Portafolio"</strong>.</li>
            <li>Filtra los resultados por fecha para ver los retornos acumulados.</li>
            <li>Descarga los datos en CSV si lo deseas.</li>
          </ul>
        </section>

        <section>
          <h2 className="flex items-center gap-2 text-xl font-semibold text-blue-700 dark:text-blue-400 mb-2">
            <BarChart3 className="w-6 h-6" /> Módulo Intraday
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-2">
            Ejecuta una estrategia de trading que combina señales diarias (GARCH) con señales intradía (RSI + Bandas de Bollinger).
          </p>
          <ul className="list-disc list-inside text-gray-700 dark:text-gray-300">
            <li>Presiona <strong>"Ejecutar estrategia"</strong> para iniciar el análisis.</li>
            <li>Selecciona fechas de inicio y fin para filtrar los retornos mostrados en la gráfica.</li>
            <li><strong>Consejo:</strong> Para ver el gráfico completo use en fecha de inicio la primera fecha disponible, y en fecha de fin la última disponible.</li>
          </ul>
        </section>

        <section>
          <h2 className="flex items-center gap-2 text-xl font-semibold text-blue-700 dark:text-blue-400 mb-2">
            <Settings className="w-6 h-6" /> Benchmarking
          </h2>
          <p className="text-gray-700 dark:text-gray-300 mb-2">
            Compara el rendimiento de ambas estrategias en versiones secuencial y paralela.
          </p>
          <ul className="list-disc list-inside text-gray-700 dark:text-gray-300">
            <li>Selecciona la estrategia: <em>Sentiment</em> o <em>Intradía</em>.</li>
            <li>Haz clic en <strong>"Obtener Datos de Benchmarking"</strong>.</li>
            <li>Observa la tabla comparativa y el gráfico de barras.</li>
            <li>Haz clic en <strong>"Recalcular"</strong> para repetir el proceso y generar de nuevo los datos.</li>
          </ul>
        </section>

        <section>
          <h2 className="flex items-center gap-2 text-xl font-semibold text-blue-700 dark:text-blue-400 mb-2">
            <Lightbulb className="w-6 h-6" /> Consejos
          </h2>
          <ul className="list-disc list-inside text-gray-700 dark:text-gray-300">
            <li>Activa el <strong>modo oscuro</strong> para una mejor experiencia visual.</li>
            <li>Si algo tarda demasiado, revisa los mensajes emergentes para más detalles.</li>
          </ul>
        </section>
      </div>
    </PageWrapper>
  );
};

export default Guide;
