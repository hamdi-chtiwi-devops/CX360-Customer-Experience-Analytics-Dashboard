import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Or your proxied URL like '/api'

const getToken = () => localStorage.getItem('token');

export const getDashboardKpis = async () => {
  const token = getToken();
  if (!token) {
    // This case should ideally be handled by ProtectedRoute before even calling this service
    // for a dashboard component. However, defensive check is good.
    console.error('No token found. Authentication might be missing.');
    throw new Error('Authentication token not found. Please login.');
  }

  const config = {
    headers: { Authorization: `Bearer ${token}` },
  };

  try {
    // Backend endpoint is /dashboard/kpis
    const response = await axios.get(`${API_URL}/dashboard/kpis`, config);
    return response.data; // Expects { total_feedback: int, average_rating: float | null }
  } catch (error) {
    console.error("Error fetching dashboard KPIs:", error.response ? error.response.data : error.message);
    // Rethrow a more generic error or the specific error message from backend if available
    const errorMessage = error.response && error.response.data && error.response.data.detail
                       ? error.response.data.detail
                       : error.message;
    throw new Error(errorMessage || 'Failed to fetch dashboard KPIs.');
  }
};

export const getRecommendations = async () => {
  const token = getToken();
  if (!token) {
    console.error('No token found for getRecommendations.');
    throw new Error('Authentication token not found. Please login.');
  }

  const config = {
    headers: { Authorization: `Bearer ${token}` },
  };

  try {
    const response = await axios.get(`${API_URL}/dashboard/recommendations`, config);
    // Assuming backend response is { recommendations: ["rec1", "rec2"] }
    return response.data.recommendations;
  } catch (error) {
    console.error("Error fetching recommendations:", error.response ? error.response.data : error.message);
    const errorMessage = error.response && error.response.data && error.response.data.detail
                       ? error.response.data.detail
                       : error.message;
    throw new Error(errorMessage || 'Failed to fetch recommendations.');
  }
};

export const getSentimentDistribution = async (params = {}) => {
  const token = getToken();
  if (!token) {
    console.error('No token found for getSentimentDistribution.');
    throw new Error('Authentication token not found. Please login.');
  }

  const queryParams = {};
  if (params.startDate) queryParams.start_date = params.startDate; // Expect YYYY-MM-DD string
  if (params.endDate) queryParams.end_date = params.endDate;     // Expect YYYY-MM-DD string

  const config = {
    headers: { Authorization: `Bearer ${token}` },
    params: queryParams
  };
  try {
    const response = await axios.get(`${API_URL}/dashboard/kpis/sentiment-distribution`, config);
    return response.data; // Expects { data: [{ label: str, count: int }] }
  } catch (error) {
    console.error("Error fetching sentiment distribution:", error.response ? error.response.data : error.message);
    const errorMessage = error.response && error.response.data && error.response.data.detail
                       ? error.response.data.detail
                       : error.message;
    throw new Error(errorMessage || 'Failed to fetch sentiment distribution.');
  }
};

export const getFeedbackCountOverTime = async (params = {}) => {
  const token = getToken();
  if (!token) {
    console.error('No token found for getFeedbackCountOverTime.');
    throw new Error('Authentication token not found. Please login.');
  }

  const queryParams = {};
  if (params.startDate) queryParams.start_date = params.startDate; // Expect YYYY-MM-DD string
  if (params.endDate) queryParams.end_date = params.endDate;     // Expect YYYY-MM-DD string

  const config = {
    headers: { Authorization: `Bearer ${token}` },
    params: queryParams
  };
  try {
    const response = await axios.get(`${API_URL}/dashboard/kpis/feedback-over-time`, config);
    return response.data; // Expects { data: [{ date: 'YYYY-MM-DD', count: int }] }
  } catch (error) {
    console.error("Error fetching feedback count over time:", error.response ? error.response.data : error.message);
    const errorMessage = error.response && error.response.data && error.response.data.detail
                       ? error.response.data.detail
                       : error.message;
    throw new Error(errorMessage || 'Failed to fetch feedback count over time.');
  }
};

export const getRatingDistribution = async (params = {}) => {
  const token = getToken();
  if (!token) {
    console.error('No token found for getRatingDistribution.');
    throw new Error('Authentication token not found. Please login.');
  }

  const queryParams = {};
  if (params.startDate) queryParams.start_date = params.startDate; // Expect YYYY-MM-DD string
  if (params.endDate) queryParams.end_date = params.endDate;     // Expect YYYY-MM-DD string

  const config = {
    headers: { Authorization: `Bearer ${token}` },
    params: queryParams
  };
  try {
    const response = await axios.get(`${API_URL}/dashboard/kpis/rating-distribution`, config);
    return response.data; // Expects { data: [{ rating: int, count: int }] }
  } catch (error) {
    console.error("Error fetching rating distribution:", error.response ? error.response.data : error.message);
    const errorMessage = error.response && error.response.data && error.response.data.detail
                       ? error.response.data.detail
                       : error.message;
    throw new Error(errorMessage || 'Failed to fetch rating distribution.');
  }
};
