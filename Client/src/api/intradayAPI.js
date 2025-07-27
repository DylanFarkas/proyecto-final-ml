import axios from 'axios';

const intradayApi = axios.create({
    baseURL: 'http://localhost:8000/intradaily',

});

export const getIntradaySignals = () => intradayApi.get('/signals');

export const getIntradayReturns = () => intradayApi.get('/returns');

export const getIntradayDates = () => intradayApi.get('/dates');

export const getFilteredIntradayReturns = (startDate, endDate) => {
  return intradayApi.get('/returns/filter', {
    params: { start_date: startDate, end_date: endDate }
  });
};

export const getIntradayPlot = () => {
  return intradayApi.get('/plot', { responseType: 'blob' });
};

export const downloadIntradayCSV = (startDate, endDate) => {
  const url = `http://localhost:8000/intradaily/returns/filter?start_date=${startDate}&end_date=${endDate}`;
  window.open(url, "_blank");
};