import React from 'react';
import FeedbackItem from './FeedbackItem';

function FeedbackList({ feedbackItems }) {
  if (!feedbackItems || feedbackItems.length === 0) {
    return <p className="text-gray-600 text-center py-4">No feedback yet. Be the first to submit!</p>;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Feedback Entries</h2>
      {feedbackItems.map((item) => (
        <FeedbackItem key={item.id} feedback={item} />
      ))}
    </div>
  );
}

export default FeedbackList;
