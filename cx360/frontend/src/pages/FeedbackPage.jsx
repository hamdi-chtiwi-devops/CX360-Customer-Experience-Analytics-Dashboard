import React, { useState, useEffect, useCallback } from 'react';
import FeedbackList from '../components/feedback/FeedbackList';
import FeedbackForm from '../components/feedback/FeedbackForm';
import { getFeedbackList, submitFeedback as apiSubmitFeedback } from '../services/feedbackService';
import { useAuth } from '../context/AuthContext'; // To potentially get user_id or token status

function FeedbackPage() {
  const [feedbackItems, setFeedbackItems] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(''); // For displaying fetch/submit errors generally
  const [formError, setFormError] = useState(''); // Specific for form submission errors
  const [formSuccessMessage, setFormSuccessMessage] = useState('');

  const { isAuthenticated, user } = useAuth(); // Get auth status and user info

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

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">Customer Feedback</h1>

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
