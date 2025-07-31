import { useState, useEffect } from "react";
import { recalculatePortfolio } from "../../api/sentimentAPI";
import { useAlert } from "../../contexts/AlertContext";

const RecalculateForm = ({ onSuccess, onCriterioChange }) => {
    const [criterio, setCriterio] = useState(() => {
        return localStorage.getItem("criterioActivo") || "engagement_ratio";
    });
    const [status, setStatus] = useState("");
    const [progress, setProgress] = useState(0);
    const [loading, setLoading] = useState(false);
    const { showError, showSuccess } = useAlert();

    const handleRecalculate = async () => {
        if (!criterio.trim()) {
            showError("Por favor seleccione un criterio válido");
            return;
        }

        setLoading(true);
        try {
            const data = await recalculatePortfolio(criterio);
            onSuccess(data);
            onCriterioChange(criterio);
            showSuccess(`Portafolio recalculado con éxito usando el criterio: ${criterio}`);
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } catch (error) {
            showError(error.message || "Error al recalcular el portafolio");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        let interval;
        if (loading) {
            interval = setInterval(async () => {
                try {
                    const res = await fetch("http://localhost:8000/sentiment/recalculate/status");
                    if (res.ok) {
                        const json = await res.json();
                        setStatus(json.status || "Procesando...");
                        setProgress(json.progress || 0);
                    }
                } catch (err) {
                    console.error("Error polling progreso:", err);
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [loading]);

    return (
        <div className="mb-6">
            <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-white">
                Criterio de análisis:
            </label>
            <select
                value={criterio}
                onChange={(e) => {
                    setCriterio(e.target.value);
                    localStorage.setItem("criterioActivo", e.target.value);
                }} 
                className="border rounded px-2 py-1 mr-4 cursor-pointer dark:bg-gray-800 text-gray-800 dark:text-gray-100 border-gray-300 dark:border-gray-600"
                disabled={loading}
            >
                <option value="engagement_ratio">Engagement Ratio</option>
                <option value="twitterLikes">Twitter Likes</option>
                <option value="twitterComments">Twitter Comments</option>
            </select>
            <button
                onClick={handleRecalculate}
                disabled={loading || !criterio.trim()}
                className="bg-blue-600 text-white px-4 py-1 rounded cursor-pointer hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {loading ? "Calculando..." : "Recalcular Portafolio"}
            </button>

            {loading && (
                <div className="mt-2 text-sm text-gray-700 dark:text-gray-300">
                    {status} ({progress}%)
                    <div className="w-full bg-gray-200 rounded h-2 mt-1 dark:bg-gray-700">
                        <div className="bg-blue-500 h-2 rounded transition-all duration-300" style={{ width: `${progress}%` }}></div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RecalculateForm;