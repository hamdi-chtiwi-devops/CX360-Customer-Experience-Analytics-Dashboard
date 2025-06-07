import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { getRatingDistribution } from '../../services/dashboardService';

const RATING_COLORS = ['#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF', '#BF55EC']; // Example colors for ratings 1-5

function RatingDistributionChart({ startDate, endDate }) { // Accept startDate and endDate as props
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        // Pass startDate and endDate to the service call
        const result = await getRatingDistribution({ startDate, endDate });

        const dataToProcess = Array.isArray(result.data) ? result.data : [];
        const formattedData = dataToProcess.map((item, index) => ({
          ...item,
          name: `Rating ${item.rating}`,
          fill: RATING_COLORS[item.rating - 1] || RATING_COLORS[index % RATING_COLORS.length],
        }));
        setChartData(formattedData);
      } catch (err) {
        setError(err.message || 'Failed to fetch rating distribution data.');
        console.error("RatingDistributionChart error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [startDate, endDate]); // Add startDate and endDate to dependency array

  if (loading) return <p className="text-center text-gray-600 py-4">Loading Rating Distribution Chart...</p>;
  if (error) return <p className="text-center text-red-500 bg-red-100 p-3 rounded-md">Error: {error}</p>;
  if (!chartData || chartData.length === 0) return <p className="text-center text-gray-500 py-4">No rating data available for the chart.</p>;

  return (
    <div className="bg-white shadow-lg rounded-xl p-6" style={{ width: '100%', height: 400 }}> {/* Increased height */}
      <h4 className="text-xl font-semibold mb-4 text-gray-700 text-center">Feedback Rating Distribution</h4>
      <ResponsiveContainer>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}> {/* Adjusted left margin */}
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }}/>
          <Tooltip
            contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'}}
          />
          <Legend wrapperStyle={{ fontSize: 14 }} />
          <Bar dataKey="count" name="Feedback Count">
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
export default RatingDistributionChart;
