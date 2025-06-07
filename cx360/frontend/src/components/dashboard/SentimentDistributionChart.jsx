import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getSentimentDistribution } from '../../services/dashboardService';

const COLORS = {
  positive: '#22c55e', // Green-500
  negative: '#ef4444', // Red-500
  neutral: '#f59e0b',  // Amber-500 (was FFBB28 - yellow)
  default: '#6b7280'   // Gray-500 for any unexpected labels
};

const RADIAN = Math.PI / 180;
const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index, payload }) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  if (percent * 100 < 5) return null; // Don't render label if slice is too small

  return (
    <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central" fontSize="12px">
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

function SentimentDistributionChart({ startDate, endDate }) {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await getSentimentDistribution({ startDate, endDate });
        const dataToProcess = Array.isArray(result.data) ? result.data : [];

        // Map data and assign colors
        const formattedData = dataToProcess.map(item => ({
          name: item.label.charAt(0).toUpperCase() + item.label.slice(1), // Capitalize label for display
          value: item.count, // Recharts Pie expects 'value' for dataKey
          fill: COLORS[item.label.toLowerCase()] || COLORS.default,
        }));
        setChartData(formattedData);
      } catch (err) {
        setError(err.message || 'Failed to fetch sentiment distribution data.');
        console.error("SentimentDistributionChart error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [startDate, endDate]);

  if (loading) return <p className="text-center text-gray-600 py-4">Loading Sentiment Distribution Chart...</p>;
  if (error) return <p className="text-center text-red-500 bg-red-100 p-3 rounded-md">Error: {error}</p>;
  if (!chartData || chartData.length === 0) return <p className="text-center text-gray-500 py-4">No sentiment data available for the chart.</p>;

  return (
    <div className="bg-white shadow-lg rounded-xl p-6" style={{ width: '100%', height: 400 }}>
      <h4 className="text-xl font-semibold mb-4 text-gray-700 text-center">Sentiment Distribution</h4>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomizedLabel}
            outerRadius={110} // Adjusted outerRadius
            fill="#8884d8"
            dataKey="value" // Use 'value' which we mapped
            nameKey="name"   // Use 'name' which we mapped
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'}}
          />
          <Legend wrapperStyle={{ fontSize: 14 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
export default SentimentDistributionChart;
