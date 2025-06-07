import React, { useState } from 'react'; // Removed useEffect as it's not directly used here now
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css"; // Import datepicker CSS

import KPIs from '../components/dashboard/KPIs';
import FeedbackCountChart from '../components/dashboard/FeedbackCountChart';
import RatingDistributionChart from '../components/dashboard/RatingDistributionChart';
import SentimentDistributionChart from '../components/dashboard/SentimentDistributionChart'; // Import new chart

function DashboardPage() {
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  // activeFilters will hold the dates that are actually applied to the charts
  const [activeFilters, setActiveFilters] = useState({ startDate: null, endDate: null });

  const handleApplyFilters = () => {
    const formattedStartDate = startDate ? startDate.toISOString().split('T')[0] : null;
    const formattedEndDate = endDate ? endDate.toISOString().split('T')[0] : null;
    setActiveFilters({ startDate: formattedStartDate, endDate: formattedEndDate });
  };

  const handleClearFilters = () => {
    setStartDate(null);
    setEndDate(null);
    setActiveFilters({ startDate: null, endDate: null }); // This will trigger re-fetch in charts with default (no) params
  };

  return (
    <div className="container mx-auto p-4 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-800 mb-2">CX360 Dashboard</h1>
        <p className="text-gray-600">
          Welcome to your central hub for customer experience insights.
        </p>
      </div>

      {/* Filter UI Section */}
      <div className="my-6 p-6 bg-white shadow-md rounded-lg border border-gray-200">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">Filter Dashboard Data</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 items-end">
          <div className="flex-grow">
            <label htmlFor="startDate" className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <DatePicker
              selected={startDate}
              onChange={(date) => setStartDate(date)}
              selectsStart
              startDate={startDate}
              endDate={endDate}
              dateFormat="yyyy-MM-dd"
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              isClearable
              placeholderText="Select start date"
            />
          </div>
          <div className="flex-grow">
            <label htmlFor="endDate" className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <DatePicker
              selected={endDate}
              onChange={(date) => setEndDate(date)}
              selectsEnd
              startDate={startDate}
              endDate={endDate}
              minDate={startDate} // Prevent end date from being before start date
              dateFormat="yyyy-MM-dd"
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              isClearable
              placeholderText="Select end date"
            />
          </div>
          <div className="flex space-x-2 sm:col-span-2 md:col-span-2 justify-start md:justify-end pt-5"> {/* Buttons aligned to end on larger screens */}
            <button
              onClick={handleApplyFilters}
              className="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Apply Filters
            </button>
            <button
              onClick={handleClearFilters}
              className="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      <KPIs /> {/* KPIs currently don't use date filters, but could be enhanced later */}

      {/* Charts Section */}
      {/* Adjusted grid to attempt 3 columns on large screens for all charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <FeedbackCountChart startDate={activeFilters.startDate} endDate={activeFilters.endDate} />
        <RatingDistributionChart startDate={activeFilters.startDate} endDate={activeFilters.endDate} />
        <SentimentDistributionChart startDate={activeFilters.startDate} endDate={activeFilters.endDate} />
      </div>

    </div>
  );
}

export default DashboardPage;
