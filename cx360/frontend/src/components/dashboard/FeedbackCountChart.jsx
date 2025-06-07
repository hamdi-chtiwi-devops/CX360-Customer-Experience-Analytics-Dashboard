import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getFeedbackCountOverTime } from '../../services/dashboardService';

function FeedbackCountChart() {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null); // Clear previous errors
        const result = await getFeedbackCountOverTime();

        // Ensure result.data is an array before mapping
        const dataToProcess = Array.isArray(result.data) ? result.data : [];

        const formattedData = dataToProcess.map(item => ({
          ...item,
          // Format date for display if needed, e.g., from 'YYYY-MM-DD' to 'MM/DD'
          // The date from backend is already 'YYYY-MM-DD' which Recharts can often handle.
          // For more specific formatting:
          date: new Date(item.date + 'T00:00:00Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' })
        }));
        setChartData(formattedData);
      } catch (err) {
        setError(err.message || 'Failed to fetch feedback count data.');
        console.error("FeedbackCountChart error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <p className="text-center text-gray-600 py-4">Loading Feedback Count Chart...</p>;
  if (error) return <p className="text-center text-red-500 bg-red-100 p-3 rounded-md">Error: {error}</p>;
  if (!chartData || chartData.length === 0) return <p className="text-center text-gray-500 py-4">No feedback data available for the chart.</p>;

  return (
    <div className="bg-white shadow-lg rounded-xl p-6" style={{ width: '100%', height: 400 }}> {/* Increased height */}
      <h4 className="text-xl font-semibold mb-4 text-gray-700 text-center">Feedback Trend (Last 30 Days)</h4>
      <ResponsiveContainer>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}> {/* Adjusted left margin */}
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'}}
          />
          <Legend wrapperStyle={{ fontSize: 14 }} />
          <Line type="monotone" dataKey="count" stroke="#4A90E2" strokeWidth={2} activeDot={{ r: 8 }} name="Feedback Count"/>
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
export default FeedbackCountChart;
