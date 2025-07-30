import { useState, useEffect } from "react";
import SentimentPage from "./pages/SentimentPage";
import IntradayPage from "./pages/IntradayPage";
import { Toaster } from "react-hot-toast";
import { Moon, Sun } from "lucide-react";
import "../index.css";
import BenchMarkingPage from "./pages/BenchMarkingPage";

const App = () => {
  const [activeTab, setActiveTab] = useState("sentiment");
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.theme === "dark" ||
      (!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches);
  });

  useEffect(() => {
    localStorage.theme = darkMode ? "dark" : "light";
  }, [darkMode]);

  return (
    <>
      <Toaster position="top-right" toastOptions={{ duration: 3000 }} />

      <div className={`${darkMode ? "dark" : ""}`}>
        <div className="min-h-screen bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-white">
          <header className="bg-white dark:bg-gray-800 shadow p-4 flex justify-between items-center">
            <h1 className="text-xl font-bold">Proyecto Final</h1>

            <div className="flex gap-4 items-center">
              <button
                onClick={() => setDarkMode(prev => !prev)}
                className="flex items-center gap-2 px-3 py-2 text-sm rounded cursor-pointer bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:opacity-90"
              >
                {darkMode ? (
                  <>
                    <Sun className="w-5 h-5" />
                    <span className="hidden sm:inline">Claro</span>
                  </>
                ) : (
                  <>
                    <Moon className="w-5 h-5" />
                    <span className="hidden sm:inline">Oscuro</span>
                  </>
                )}
              </button>

              <nav className="space-x-2">
                <button
                  onClick={() => setActiveTab("sentiment")}
                  className={`px-3 py-2 rounded cursor-pointer ${activeTab === "sentiment"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 dark:bg-gray-700 dark:text-white"
                    }`}
                >
                  Sentiment
                </button>
                <button
                  onClick={() => setActiveTab("intraday")}
                  className={`px-3 py-2 rounded cursor-pointer ${activeTab === "intraday"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 dark:bg-gray-700 dark:text-white"
                    }`}
                >
                  Intraday
                </button>
                <button
                  onClick={() => setActiveTab("benchmarking")}
                  className={`px-3 py-2 rounded cursor-pointer ${activeTab === "benchmarking"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 dark:bg-gray-700 dark:text-white"
                    }`}
                >
                  Benchmarking
                </button>
              </nav>
            </div>
          </header>

          <main className="p-6">
            {activeTab === "sentiment" && <SentimentPage />}
            {activeTab === "intraday" && <IntradayPage />}
            {activeTab === "benchmarking" && <BenchMarkingPage />}
          </main>
        </div>
      </div>
    </>
  );
};

export default App;
