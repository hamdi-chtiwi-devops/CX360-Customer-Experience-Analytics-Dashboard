import React, { useState, useEffect } from 'react';
import { getDashboardKpis } from '../../services/dashboardService'; // Adjusted path

function KPIs() {
  const [kpis, setKpis] = useState({ total_feedback: 0, average_rating: null });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchKpis = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await getDashboardKpis();
        setKpis({
          total_feedback: data.total_feedback !== undefined ? data.total_feedback : 0,
          average_rating: data.average_rating !== undefined ? data.average_rating : null,
        });
      } catch (err) {
        setError(err.message || 'Failed to fetch KPIs. Please ensure you are logged in and the server is running.');
        console.error("KPI fetch error:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchKpis();
  }, []); // Empty dependency array means this effect runs once on mount

  const kpiCardBaseStyle = "bg-white shadow-lg rounded-xl p-6 text-center transform transition-all hover:scale-105";
  const kpiValueBaseStyle = "text-4xl font-bold mt-2";
  const kpiTitleBaseStyle = "text-md text-gray-500";


  if (isLoading) {
    return <p className="text-center text-gray-600 py-4">Loading KPIs...</p>;
  }

  if (error) {
    return <p className="text-center text-red-500 bg-red-100 p-3 rounded-md">Error fetching KPIs: {error}</p>;
  }

  return (
    <div className="mb-8">
      <h3 className="text-2xl font-semibold text-gray-800 mb-6">Key Performance Indicators</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className={`${kpiCardBaseStyle} border-t-4 border-blue-500`}>
          <h4 className={kpiTitleBaseStyle}>Total Feedback Entries</h4>
          <p className={`${kpiValueBaseStyle} text-blue-600`}>{kpis.total_feedback}</p>
        </div>
        <div className={`${kpiCardBaseStyle} border-t-4 border-green-500`}>
          <h4 className={kpiTitleBaseStyle}>Average Customer Rating</h4>
          <p className={`${kpiValueBaseStyle} text-green-600`}>
            {kpis.average_rating !== null ? kpis.average_rating.toFixed(1) : 'N/A'}
          </p>
        </div>
        {/* Add more KPI cards here as needed, e.g.:
        <div className={`${kpiCardBaseStyle} border-t-4 border-purple-500`}>
          <h4 className={kpiTitleBaseStyle}>New Feedback (Last 7 Days)</h4>
          <p className={`${kpiValueBaseStyle} text-purple-600`}>0</p>
        </div>
        */}
      </div>
    </div>
  );
}

export default KPIs;
