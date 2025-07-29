import axios from 'axios';

const sentimentApi = axios.create({
    baseURL: 'http://localhost:8000/sentiment',
})

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