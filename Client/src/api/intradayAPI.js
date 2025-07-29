import axios from 'axios';

const intradayApi = axios.create({
  baseURL: 'http://localhost:8000/intradaily/',
});

export const runIntradayStrategy = async () => {
  try {
    const response = await intradayApi.post('run-strategy/');
    return response.data; 
  } catch (error) {
    console.error('Error ejecutando estrategia intradía:', error);
    throw error;
  }
};

export const getAvailableDates = async () => {
  try {
    const response = await intradayApi.get('dates');
    return response.data.dates; 
  } catch (error) {
    console.error('Error obteniendo fechas:', error);
    throw error;
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
    console.error('Error al obtener retornos:', error);
    throw error;
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
    console.error('Error al obtener retornos diarios:', error);
    throw error;
  }
};

export const getDownloadLink = (startDate, endDate, tipoRetorno) => {
  const params = new URLSearchParams();
  if (startDate) params.append("start_date", startDate);
  if (endDate) params.append("end_date", endDate);
  params.append("tipo", tipoRetorno);

  return `http://localhost:8000/intradaily/returns/download?${params.toString()}`;
};
