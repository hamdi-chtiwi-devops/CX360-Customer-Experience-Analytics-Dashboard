import React from 'react';
import KPIs from '../components/dashboard/KPIs';

function DashboardPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">CX360 Dashboard</h1>
      <p className="text-gray-600 mb-8">
        Welcome to your central hub for customer experience insights.
      </p>
      {/* KPIs component already has its own mb-8 for spacing below it */}
      <KPIs />

      {/* Placeholder for future components */}
      {/* <div className="mt-8">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Recent Feedback</h2>
        {/* <RecentFeedbackList /> Placeholder for another component }
        <p className="text-gray-500">Recent feedback display coming soon...</p>
      </div> */}
    </div>
  );
}

export default DashboardPage;
