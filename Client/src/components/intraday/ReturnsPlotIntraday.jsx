import React from 'react';

const ReturnsPlotIntraday = ({ plotUrl }) => {
  return (
    <div className="my-6">
      <h3 className="text-lg font-semibold mb-2">Retorno Acumulado</h3>
      <img
        src={plotUrl}
        alt="Gráfico del retorno acumulado"
        className="w-full max-w-4xl mx-auto border rounded shadow"
      />
    </div>
  );
};

export default ReturnsPlotIntraday;
