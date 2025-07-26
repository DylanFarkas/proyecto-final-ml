import { useEffect, useState } from "react";
import { getSentimentReturns } from "../../api/sentimentAPI";

const ReturnsTable = () => {
  const [returns, setReturns] = useState([]);

  useEffect(() => {
    const fetchReturns = async () => {
      try {
        const response = await getSentimentReturns();
        setReturns(response.data);
      } catch (error) {
        console.error("Error fetching returns:", error);
      }
    };
    fetchReturns();
  }, []);

  return (
    <div className="overflow-x-auto shadow-md rounded-lg bg-gray-50 dark:bg-gray-900">
      <table className="min-w-full text-sm text-left text-gray-800 dark:text-gray-100">
        <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 uppercase text-xs">
          <tr>
            <th className="px-6 py-3">Fecha</th>
            <th className="px-6 py-3">Portafolio</th>
            <th className="px-6 py-3">Nasdaq</th>
          </tr>
        </thead>
        <tbody>
          {returns.map((row, idx) => (
            <tr className={idx % 2 === 0 ? "bg-white dark:bg-gray-900" : "bg-gray-50 dark:bg-gray-800"}>

              <td className="px-6 py-4 whitespace-nowrap">{row.Date}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                {row.portfolio_returns.toFixed(4)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {row.nasdaq_return.toFixed(4)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

  );
};

export default ReturnsTable;
