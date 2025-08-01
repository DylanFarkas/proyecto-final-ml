import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid
} from "recharts";

const InteractivePlot = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="Date" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="portfolio_returns" name="Portafolio" stroke="#1D4ED8" strokeWidth={2} />
        <Line type="monotone" dataKey="nasdaq_return" name="Nasdaq" stroke="#AD46FF" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default InteractivePlot;