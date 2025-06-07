import React from 'react';

function FeedbackItem({ feedback }) {
  if (!feedback) {
    return null;
  }

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 mb-4 border border-gray-200">
      <p className="text-gray-800 text-lg mb-3">{feedback.feedback_text}</p>

      <div className="text-sm text-gray-600 space-y-1">
        {feedback.rating && (
          <p><strong>Rating:</strong> <span className="font-semibold text-indigo-600">{feedback.rating}/5</span></p>
        )}
        {feedback.customer_name && (
          <p><strong>From:</strong> {feedback.customer_name}</p>
        )}
        {feedback.email && (
          <p><strong>Email:</strong> {feedback.email}</p>
        )}
        {feedback.source && (
          <p><strong>Source:</strong> {feedback.source}</p>
        )}
        <p><strong>Date:</strong> {new Date(feedback.created_at).toLocaleString()}</p>
        {feedback.user_id && (
          <p><strong>User ID:</strong> {feedback.user_id}</p>
        )}
      </div>

      {/* Sentiment Display */}
      {feedback.sentiment_label && (
        <div className="mt-4 pt-3 border-t border-gray-200"> {/* Added border-t for separation */}
          <span
            className={`px-3 py-1 text-xs font-bold rounded-full leading-none
                        ${feedback.sentiment_label === 'positive' ? 'bg-green-100 text-green-800' :
                          feedback.sentiment_label === 'negative' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800' // Default/neutral
                        }`}
          >
            Sentiment: {feedback.sentiment_label.charAt(0).toUpperCase() + feedback.sentiment_label.slice(1)}
            {typeof feedback.sentiment_score === 'number' && ` (${feedback.sentiment_score.toFixed(2)})`}
          </span>
        </div>
      )}
    </div>
  );
}

export default FeedbackItem;
