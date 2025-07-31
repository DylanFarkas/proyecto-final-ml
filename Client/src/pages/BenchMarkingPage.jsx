import React, { useState, useEffect } from 'react';
import { getComparisonData } from '../api/sentimentAPI';
import { getComparisonIntradayData, getDownloadProgress as getIntradailyDownloadProgress } from '../api/intradayAPI';
import { getDownloadSentimentProgress } from '../api/sentimentAPI'; 
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Swal from 'sweetalert2';
import PageWrapper from '../components/common/PageWrapper';

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

            if (selectedApp === "sentiment") {
                data = await getComparisonData();
            } else {
                data = await getComparisonIntradayData(); 
            }

            localStorage.setItem(`comparisonData_${selectedApp}`, JSON.stringify(data));
            setComparisonData(data);

            Swal.fire({
                title: "¡Datos obtenidos correctamente!",
                text: "La comparación de rendimiento se ha cargado con éxito",
                icon: "success",
                confirmButtonText: "Aceptar",
                confirmButtonColor: "#2563eb",
            });

        } catch (error) {
            console.error('Error al obtener la comparación de rendimiento:', error);
            setError(error.message || 'Hubo un error al obtener los datos.');
            
            // Determinar el tipo de error para mostrar diferentes alertas
            let errorTitle = "Error";
            let errorIcon = "error";
            let errorText = error.message || 'Hubo un problema al obtener los datos de la comparación';
            
            if (error.message?.includes('Timeout') || error.message?.includes('⏱️')) {
                errorTitle = "Operación Lenta";
                errorIcon = "warning";
                errorText = error.message;
            } else if (error.message?.includes('Archivo no encontrado') || error.message?.includes('📁')) {
                errorTitle = "Archivos No Encontrados";
                errorIcon = "info";
                errorText = error.message;
            } else if (error.message?.includes('Error de conexión') || error.message?.includes('🌐')) {
                errorTitle = "Problema de Conexión";
                errorIcon = "error";
                errorText = error.message;
            }
            
            Swal.fire({
                title: errorTitle,
                text: errorText,
                icon: errorIcon,
                confirmButtonText: "Aceptar",
                confirmButtonColor: "#dc2626",
                footer: selectedApp === "sentiment" ? 
                    '<small>Asegúrese de que el archivo sentiment_data.csv esté disponible</small>' :
                    '<small>Asegúrese de que los archivos de datos intradía estén disponibles</small>'
            });
        } finally {
            setLoading(false);
        }
    };

    const fetchDownloadProgress = async () => {
        try {
            if (selectedApp === "sentiment") {
                const response = await getDownloadSentimentProgress(); 
                setDownloadProgress(response.progress); 
            } else {
                const response = await getIntradailyDownloadProgress(); 
                setDownloadProgress(response.progress); 
            }
        } catch (error) {
            console.error('Error obteniendo el progreso de descarga:', error);
        }
    };

    useEffect(() => {
        if (loading) {
            const interval = setInterval(fetchDownloadProgress, 1000); // Actualiza cada 1 segundo
            return () => clearInterval(interval); // Limpia el intervalo cuando se detiene la carga
        }
    }, [loading]);

    const handleRecalculate = () => {
        localStorage.removeItem(`comparisonData_${selectedApp}`);
        fetchComparisonData();
    };

    const chartData = comparisonData ? [
        {
            name: 'Secuencial',
            tiempo: comparisonData.secuencial.tiempo,
            cpu: comparisonData.secuencial.cpu,
        },
        {
            name: 'Paralelo',
            tiempo: comparisonData.paralelo.tiempo,
            cpu: comparisonData.paralelo.cpu,
        },
    ] : [];

    return (
        <PageWrapper pageName="Benchmarking">
            <div className="p-6 bg-white dark:bg-gray-800 rounded-md shadow-md">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-5">Benchmarking</h1>

            <label className="block text-sm font-medium text-gray-700 dark:text-white mb-2">Seleccionar Aplicación</label>
            <select
                value={selectedApp}
                onChange={(e) => setSelectedApp(e.target.value)} 
                className="border rounded px-4 py-2 mb-4 mr-5 cursor-pointer text-gray-700 dark:bg-gray-800 dark:text-white"
            >
                <option value="sentiment">Sentiment Analysis</option>
                <option value="intradaily">Estrategia Intradía</option>
            </select>

            <button
                onClick={fetchComparisonData}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md cursor-pointer hover:bg-blue-700 disabled:opacity-50"
            >
                {loading ? 'Cargando...' : 'Obtener Datos de Benchmarking'}
            </button>

            <button
                onClick={handleRecalculate}
                disabled={loading}
                className="bg-red-600 text-white px-4 py-2 rounded-md cursor-pointer hover:bg-red-700 disabled:opacity-50 ml-4"
            >
                Recalcular
            </button>

            {/* Mostrar mensaje de error con más detalles */}
            {error && (
                <div className="mt-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md p-4">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <span className="text-red-400">❌</span>
                        </div>
                        <div className="ml-3">
                            <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                                Error en el proceso de benchmarking
                            </h3>
                            <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                                <p>{error}</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Barra de progreso */}
            {loading && (
                <div className="mt-4">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        ⏳ Descargando datos... Se ejecutará primero la versión secuencial y luego la paralela
                    </h3>
                    <div className="bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded-md p-4 mb-4">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <span className="text-yellow-400">⚠️</span>
                            </div>
                            <div className="ml-3">
                                <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                                    Esta operación puede tardar varios minutos
                                </h3>
                                <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                                    <p>
                                        • El benchmarking ejecuta ambos pipelines (secuencial y paralelo)<br/>
                                        • Puede tardar hasta 3 minutos dependiendo de los datos<br/>
                                        • Si la operación tarda demasiado, recibirá una notificación
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div
                            className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                            style={{ width: `${downloadProgress}%` }}
                        />
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
                        Progreso: {downloadProgress}% {downloadProgress < 50 ? '(Ejecutando versión secuencial...)' : '(Ejecutando versión paralela...)'}
                    </p>
                </div>
            )}

            {comparisonData && (
                <div className="mt-6">
                    <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Comparación de Rendimiento: Secuencial vs Paralelo</h2>

                    {/* Tabla de comparación */}
                    <table className="min-w-full bg-white dark:bg-gray-700 rounded-md shadow-md">
                        <thead>
                            <tr className="border-b">
                                <th className="px-4 py-2 text-left text-gray-900 dark:text-white">Método</th>
                                <th className="px-4 py-2 text-left text-gray-900 dark:text-white">Tiempo (segundos)</th>
                                <th className="px-4 py-2 text-left text-gray-900 dark:text-white">Uso de CPU (%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr className="border-b">
                                <td className="px-4 py-2 text-gray-900 dark:text-white">Secuencial</td>
                                <td className="px-4 py-2 text-gray-900 dark:text-white">{comparisonData.secuencial.tiempo}</td>
                                <td className="px-4 py-2 text-gray-900 dark:text-white">{comparisonData.secuencial.cpu}</td>
                            </tr>
                            <tr className="border-b">
                                <td className="px-4 py-2 text-gray-900 dark:text-white">Paralelo</td>
                                <td className="px-4 py-2 text-gray-900 dark:text-white">{comparisonData.paralelo.tiempo}</td>
                                <td className="px-4 py-2 text-gray-900 dark:text-white">{comparisonData.paralelo.cpu}</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    {/* Gráfico con Recharts - Gráfico de barras */}
                    <div className="mt-6">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Comparación Gráfica: Secuencial vs Paralelo</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="tiempo" fill="#2B7FFF" barSize={30} />
                                <Bar dataKey="cpu" fill="#82ca9d" barSize={30} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
            </div>
        </PageWrapper>
    );
}

export default BenchMarkingPage;
