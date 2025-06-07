import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Or your proxied URL like '/api' if you set up vite proxy

const getToken = () => localStorage.getItem('token');

export const getFeedbackList = async () => {
  const token = getToken();
  // Backend GET /feedback/ might be public or protected depending on your design.
  // If protected, Authorization header is needed. If public, it might not be.
  // For now, let's assume it might be protected or that sending the token anyway is fine.
  const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

  try {
    const response = await axios.get(`${API_URL}/feedback/`, config);
    return response.data; // Expects a list of feedback items
  } catch (error) {
    console.error("Error fetching feedback list:", error.response ? error.response.data : error.message);
    throw error; // Re-throw to be caught by the caller
  }
};

export const submitFeedback = async (feedbackData) => {
  const token = getToken();
  // Backend POST /feedback/ can be anonymous or user-associated.
  // If user_id is to be associated from backend based on token, token is essential.
  const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

  // feedbackData: { feedback_text, rating, customer_name, email, source }
  // The backend will associate user_id from the token if provided and logic exists
  try {
    const response = await axios.post(`${API_URL}/feedback/`, feedbackData, config);
    return response.data; // Expects the created feedback item
  } catch (error) {
    console.error("Error submitting feedback:", error.response ? error.response.data : error.message);
    throw error; // Re-throw to be caught by the caller
  }
};
