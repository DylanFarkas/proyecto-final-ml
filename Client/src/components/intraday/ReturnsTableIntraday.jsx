import React from 'react';

const ReturnsTableIntraday = ({ data }) => {
  if (!data || data.length === 0) return <p>No hay datos disponibles.</p>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm text-left text-gray-800">
        <thead className="bg-blue-100 text-gray-700 uppercase text-xs">
          <tr>
            <th className="px-4 py-2">Fecha</th>
            <th className="px-4 py-2">Retorno</th>
            <th className="px-4 py-2">Retorno Acumulado</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              <td className="px-4 py-2">{row.datetime}</td>
              <td className="px-4 py-2">{row.strategy_return.toFixed(4)}</td>
              <td className="px-4 py-2">{row.cumulative_strategy_return.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ReturnsTableIntraday;
