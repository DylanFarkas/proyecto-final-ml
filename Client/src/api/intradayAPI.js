import axios from 'axios';

const intradayApi = axios.create({
  baseURL: 'http://localhost:8000/intradaily/',
  timeout: 30000, 
});

// Añadir interceptor para requests
intradayApi.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Añadir interceptor para responses
intradayApi.interceptors.response.use(
  (response) => {
    console.log(`[API Success] ${response.config.method?.toUpperCase()} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}:`, error.message);
    return Promise.reject(error);
  }
);

// Helper function to handle API errors
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.detail || 'Error en el servidor';
    throw new Error(`${message} (${error.response.status})`);
  } else if (error.request) {
    // Network error - could be CORS or connection issue
    const errorMessage = error.message?.toLowerCase() || '';
    if (errorMessage.includes('cors') || errorMessage.includes('access-control-allow-origin')) {
      throw new Error('Usuario no autorizado para realizar peticiones');
    }
    throw new Error('Error de conexión. Verifique su conexión a internet.');
  } else {
    // Other error
    throw new Error('Error inesperado. Intente nuevamente.');
  }
};

export const runIntradayStrategy = async () => {
  try {
    const response = await intradayApi.post('run-strategy/');
    return response.data; 
  } catch (error) {
    handleApiError(error);
  }
};

export const getAvailableDates = async () => {
  try {
    const response = await intradayApi.get('dates');
    return response.data.dates; 
  } catch (error) {
    handleApiError(error);
  }
};

export const getReturns = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await intradayApi.get('returns', { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getDailyReturns = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await intradayApi.get('returns/daily', { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getDownloadLink = (startDate, endDate, tipoRetorno) => {
  const params = new URLSearchParams();
  if (startDate) params.append("start_date", startDate);
  if (endDate) params.append("end_date", endDate);
  params.append("tipo", tipoRetorno);

  return `http://54.235.46.202:8000/intradaily/returns/download?${params.toString()}`;
};

export const getComparisonIntradayData = async () => {
  try {
    const response = await intradayApi.get('/compare');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getDownloadProgress = async () => {
  try {
    const response = await intradayApi.get('download/progress');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};