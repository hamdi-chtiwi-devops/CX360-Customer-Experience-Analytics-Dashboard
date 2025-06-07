import React, { useState, useEffect } from 'react';
import { getRecommendations } from '../../services/dashboardService'; // Adjust path if necessary

function Recommendations() {
  const [recommendationsList, setRecommendationsList] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await getRecommendations();
        setRecommendationsList(Array.isArray(data) ? data : []); // Ensure data is an array
      } catch (err) {
        setError(err.message || 'Failed to fetch recommendations');
        console.error("Recommendations fetch error:", err);
        setRecommendationsList([]); // Clear list on error or set to empty if error occurs
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, []); // Empty dependency array means this effect runs once on mount

  if (isLoading) {
    return <p className="text-sm text-center text-gray-500 py-3">Loading recommendations...</p>;
  }

  if (error) {
    return <p className="text-sm text-center text-red-600 bg-red-50 p-3 rounded-md">Error: {error}</p>;
  }

  if (recommendationsList.length === 0) {
    return (
      <div className="bg-white shadow-lg rounded-xl p-6 mt-8 border border-gray-200">
        <h4 className="text-xl font-semibold mb-3 text-gray-700 text-center">Recommendations</h4>
        <p className="text-sm text-center text-gray-500 py-3">No recommendations available at the moment.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-lg rounded-xl p-6 mt-8 border border-gray-200">
      <h4 className="text-xl font-semibold mb-4 text-gray-700 text-center">Actionable Insights & Recommendations</h4>
      <ul className="list-disc list-inside space-y-3 pl-2">
        {recommendationsList.map((rec, index) => (
          <li key={index} className="text-md text-gray-700 leading-relaxed hover:text-indigo-600 transition-colors duration-150">
            <span className="font-medium text-indigo-500 mr-1">💡</span> {rec}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Recommendations;
