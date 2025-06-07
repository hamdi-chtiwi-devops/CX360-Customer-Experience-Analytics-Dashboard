import React from 'react';
import KPIs from '../components/dashboard/KPIs';
import FeedbackCountChart from '../components/dashboard/FeedbackCountChart';
import RatingDistributionChart from '../components/dashboard/RatingDistributionChart';

function DashboardPage() {
  return (
    <div className="container mx-auto p-4 space-y-8"> {/* Added space-y for vertical spacing */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800 mb-2">CX360 Dashboard</h1>
        <p className="text-gray-600">
          Welcome to your central hub for customer experience insights.
        </p>
      </div>

      <KPIs />

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <FeedbackCountChart />
        <RatingDistributionChart />
      </div>

      {/* Placeholder for future components like recent feedback table */}
      {/* <div className="mt-8">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Recent Feedback</h2>
        <p className="text-gray-500 bg-white shadow rounded-lg p-4">Recent feedback display coming soon...</p>
      </div> */}
    </div>
  );
}

export default DashboardPage;
