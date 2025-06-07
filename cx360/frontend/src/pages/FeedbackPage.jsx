import React, { useState, useEffect, useCallback } from 'react';
import FeedbackList from '../components/feedback/FeedbackList';
import FeedbackForm from '../components/feedback/FeedbackForm';
import FeedbackCsvUpload from '../components/feedback/FeedbackCsvUpload';
import { getFeedbackList, submitFeedback as apiSubmitFeedback, exportFeedbackCsv } from '../services/feedbackService'; // Added exportFeedbackCsv
import { useAuth } from '../context/AuthContext';

function FeedbackPage() {
  const [feedbackItems, setFeedbackItems] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [formSuccessMessage, setFormSuccessMessage] = useState('');
  const [isExporting, setIsExporting] = useState(false); // State for export loading
  const [exportError, setExportError] = useState(null);   // State for export error

  const { isAuthenticated, user } = useAuth();

  const fetchFeedback = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await getFeedbackList();
      setFeedbackItems(data);
    } catch (err) {
      setError('Failed to fetch feedback. Please try again later.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFeedback();
  }, [fetchFeedback]);

  const handleSubmitFeedback = async (feedbackData) => {
    setFormError('');
    setFormSuccessMessage('');
    // If the user is authenticated, their user_id will be associated on the backend via token.
    // feedbackData from the form might include customer_name, email, etc.
    // It does not need to explicitly include user_id from frontend.
    try {
      const newFeedback = await apiSubmitFeedback(feedbackData);
      setFeedbackItems(prevItems => [newFeedback, ...prevItems]); // Optimistically add to list
      setFormSuccessMessage('Feedback submitted successfully!');
      // Potentially clear the form fields here if FeedbackForm doesn't do it itself
      // Or, FeedbackForm can be given a key that changes on success to force re-render.
    } catch (err) {
      setFormError('Failed to submit feedback. Please try again.');
      console.error(err);
    }
  };

  };

  const handleExport = async () => {
    setIsExporting(true);
    setExportError(null);
    try {
      const response = await exportFeedbackCsv(); // This is the full Axios response

      // Create a Blob from the response data
      const blob = new Blob([response.data], { type: response.headers['content-type'] || 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      let filename = 'feedback_export.csv'; // Default filename
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/i);
        if (filenameMatch && filenameMatch.length > 1) {
          filename = filenameMatch[1];
        }
      }
      link.setAttribute('download', filename);

      document.body.appendChild(link);
      link.click();

      // Cleanup: remove link and revoke URL
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error("Export error:", err);
      // err.message is from the service where we processed potential blob errors
      setExportError(err.message || 'Failed to export CSV.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">Customer Feedback</h1>

      {/* Actions Section: Upload and Export */}
      {isAuthenticated && (
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-8 p-4 bg-gray-50 rounded-lg shadow">
          <div className="flex-1 w-full sm:w-auto"> {/* Ensure CsvUpload takes available space or define specific width */}
             <FeedbackCsvUpload onUploadSuccess={fetchFeedback} />
          </div>
          <div className="flex-1 w-full sm:w-auto sm:text-right"> {/* Align button to the right on larger screens */}
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="w-full sm:w-auto px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              {isExporting ? 'Exporting...' : 'Export All as CSV'}
            </button>
            {exportError && <p className="text-red-500 text-sm mt-2 text-center sm:text-right">{exportError}</p>}
          </div>
        </div>
      )}

      {/* Section for Manual Feedback Form */}
      <div className="mb-8">
        <FeedbackForm
          onSubmitFeedback={handleSubmitFeedback}
          error={formError}
          successMessage={formSuccessMessage}
        />
      </div>

      {/* Displaying Feedback List */}
      {isLoading && <p className="text-center text-gray-600">Loading feedback...</p>}
      {error && <p className="text-center text-red-500 bg-red-100 p-3 rounded-md">{error}</p>}
      {!isLoading && !error && (
        feedbackItems.length > 0
          ? <FeedbackList feedbackItems={feedbackItems} />
          : <p className="text-center text-gray-500">No feedback has been submitted yet.</p>
            // This message is now redundant if FeedbackList handles empty state, but can be kept for clarity on page level.
      )}
    </div>
  );
}

export default FeedbackPage;
