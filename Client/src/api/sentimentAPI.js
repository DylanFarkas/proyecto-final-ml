import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL;

const sentimentApi = axios.create({
  baseURL: 'http://34.207.166.255:8000/sentiment/',
  timeout: 180000, // 3 minutos de timeout para operaciones largas como benchmarking
});

// Añadir interceptor para requests
sentimentApi.interceptors.request.use(
  (config) => {
    // Log request para debugging
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Añadir interceptor para responses
sentimentApi.interceptors.response.use(
  (response) => {
    // Log successful response
    console.log(`[API Success] ${response.config.method?.toUpperCase()} ${response.config.url}`);
    return response;
  },
  (error) => {
    // Log error response
    console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}:`, error.message);
    return Promise.reject(error);
  }
);

console.log(baseURL);

// Helper function to handle API errors
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const errorData = error.response.data;
    
    // Check if error has structured format from our API
    if (errorData && typeof errorData === 'object' && errorData.error) {
      const { error: errorType, message, details } = errorData;
      
      switch (errorType) {
        case 'timeout':
          throw new Error(`⏱️ Timeout: ${message}. La operación tardó demasiado en completarse.`);
        case 'execution_error':
          throw new Error(`❌ Error de ejecución: ${message}. Detalles: ${details}`);
        case 'file_not_found':
          throw new Error(`📁 Archivo no encontrado: ${message}. Verifique que los archivos de datos estén disponibles.`);
        case 'unexpected_error':
          throw new Error(`🚨 Error inesperado: ${message}. Detalles: ${details}`);
        default:
          throw new Error(`🔧 Error del servidor: ${message} (${error.response.status})`);
      }
    }
    
    // Fallback to old format
    const message = errorData?.detail || errorData?.message || 'Error en el servidor';
    throw new Error(`${message} (${error.response.status})`);
  } else if (error.request) {
    // Network error - could be CORS or connection issue
    const errorMessage = error.message?.toLowerCase() || '';
    if (errorMessage.includes('cors') || errorMessage.includes('access-control-allow-origin')) {
      throw new Error('🚫 Usuario no autorizado para realizar peticiones');
    }
    throw new Error('🌐 Error de conexión. Verifique su conexión a internet.');
  } else {
    // Other error
    throw new Error(`🔧 Error inesperado: ${error.message || 'Error desconocido'}`);
  }
};

export const getSentimentReturns = async () => {
  try {
    return await sentimentApi.get('/returns');
  } catch (error) {
    handleApiError(error);
  }
};

export const getPlot = async () => {
  try {
    return await sentimentApi.get('/plot', { responseType: 'blob' });
  } catch (error) {
    handleApiError(error);
  }
};

export const getFilteredReturns = async (startDate, endDate) => {
  try {
    return await sentimentApi.get('/returns/filter', {
      params: { start_date: startDate, end_date: endDate }
    });
  } catch (error) {
    handleApiError(error);
  }
};

export const getStats = async () => {
  try {
    return await sentimentApi.get('/returns/stats');
  } catch (error) {
    handleApiError(error);
  }
};

export const getAvailableDates = async () => {
  try {
    return await sentimentApi.get('/returns/dates');
  } catch (error) {
    handleApiError(error);
  }
};

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
    handleApiError(error);
  }
};

export const recalculatePortfolio = async (criterio) => {
  try {
    const res = await sentimentApi.post('/recalculate', { criterio });
    return res.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getComparisonData = async () => {
  try {
    const response = await sentimentApi.get('/compare');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getDownloadSentimentProgress = async () => {
  try {
    const response = await sentimentApi.get('download/progress');
    return response.data; 
  } catch (error) {
    handleApiError(error);
  }
};