import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL;

const sentimentApi = axios.create({
  baseURL: 'http://54.235.46.202:8000/sentiment/',
});

console.log(baseURL);

export const getSentimentReturns = () => sentimentApi.get('/returns');

export const getPlot = () => sentimentApi.get('/plot', { responseType: 'blob' });

export const getFilteredReturns = (startDate, endDate) => {
    return sentimentApi.get('/returns/filter', {
        params: { start_date: startDate, end_date: endDate }
    });
}

export const getStats = () => sentimentApi.get('/returns/stats');

export const getAvailableDates = () => sentimentApi.get('/returns/dates');

export const downloadFilteredReturnsCSV = async (startDate, endDate) => {
    try {
        const response = await sentimentApi.get('/returns/filter/csv', {
            params: { start_date: startDate, end_date: endDate },
            responseType: 'blob'
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `filtered_returns_${startDate}_to_${endDate}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error al descargar CSV:', error);
    }
};

export const recalculatePortfolio = async (criterio) => {
    try {
        const res = await sentimentApi.post('/recalculate', { criterio })
        return res.data;
    } catch (error) {
        console.error('Error al recalcular el portafolio:', error);
        throw error;
    }
}

export const getComparisonData = async () => {
    try {
        const response = await sentimentApi.get('/compare');
        return response.data;
    } catch (error) {
        console.error('Error al obtener la comparación de rendimiento:', error);
        throw error;
    }
};

export const getDownloadSentimentProgress = async () => {
    try {
        const response = await sentimentApi.get('download/progress'); // Llama al API para obtener el progreso
        return response.data; 
    } catch (error) {
        console.error('Error obteniendo el progreso de descarga:', error);
        throw error;
    }
};