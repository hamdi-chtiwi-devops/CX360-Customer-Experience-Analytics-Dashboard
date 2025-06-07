import React, { useState } from 'react';

function FeedbackForm({ onSubmitFeedback, error, successMessage }) {
  const [feedbackText, setFeedbackText] = useState('');
  const [rating, setRating] = useState(''); // Default to no rating
  const [customerName, setCustomerName] = useState('');
  const [email, setEmail] = useState('');
  const [source, setSource] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!feedbackText) {
      // Or handle this with an internal error state for the form
      alert('Feedback text cannot be empty!');
      return;
    }
    onSubmitFeedback({
      feedback_text: feedbackText,
      rating: rating ? parseInt(rating, 10) : null, // Ensure rating is integer or null
      customer_name: customerName || null,
      email: email || null,
      source: source || null,
    });
    // Optionally clear form fields after submission if parent doesn't unmount/remount
    // setFeedbackText('');
    // setRating('');
    // setCustomerName('');
    // setEmail('');
    // setSource('');
  };

  const commonInputClasses = "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";

  return (
    <form onSubmit={handleSubmit} className="p-6 bg-white shadow-md rounded-lg border border-gray-200 space-y-6">
      <h2 className="text-2xl font-semibold text-gray-800 text-center">Submit Your Feedback</h2>
      {error && <p className="text-red-500 text-sm text-center">Error: {error}</p>}
      {successMessage && <p className="text-green-600 text-sm text-center">{successMessage}</p>}

      <div>
        <label htmlFor="feedbackText" className="block text-sm font-medium text-gray-700">Feedback:*</label>
        <textarea
          id="feedbackText"
          value={feedbackText}
          onChange={(e) => setFeedbackText(e.target.value)}
          required
          rows="4"
          className={commonInputClasses}
        />
      </div>

      <div>
        <label htmlFor="rating" className="block text-sm font-medium text-gray-700">Rating (1-5):</label>
        <select
          id="rating"
          value={rating}
          onChange={(e) => setRating(e.target.value)}
          className={commonInputClasses}
        >
          <option value="">Select a rating</option>
          <option value="1">1 - Poor</option>
          <option value="2">2 - Fair</option>
          <option value="3">3 - Good</option>
          <option value="4">4 - Very Good</option>
          <option value="5">5 - Excellent</option>
        </select>
      </div>

      <div>
        <label htmlFor="customerName" className="block text-sm font-medium text-gray-700">Your Name (Optional):</label>
        <input
          type="text"
          id="customerName"
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
          className={commonInputClasses}
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">Your Email (Optional):</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={commonInputClasses}
        />
      </div>

      <div>
        <label htmlFor="source" className="block text-sm font-medium text-gray-700">Source (e.g., Website, App):</label>
        <input
          type="text"
          id="source"
          value={source}
          onChange={(e) => setSource(e.target.value)}
          className={commonInputClasses}
        />
      </div>

      <button
        type="submit"
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Submit Feedback
      </button>
    </form>
  );
}

export default FeedbackForm;
