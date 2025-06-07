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

export const exportFeedbackCsv = async () => {
  const token = getToken();
  if (!token) {
    console.error('No token found for CSV export.');
    throw new Error('Authentication token not found. Please login.');
  }

  const config = {
    headers: { Authorization: `Bearer ${token}` },
    responseType: 'blob', // Important for file downloads
  };

  try {
    const response = await axios.get(`${API_URL}/feedback/export-csv`, config);
    return response; // Return the full Axios response object (contains data as blob and headers)
  } catch (error) {
    console.error("Error exporting CSV:", error.response ? error.response.data : error.message);
    // Try to parse error from blob if server sends error as blob (unlikely for GET errors but possible)
    // For now, assume error details are in standard error properties or a generic message.
    const errorMessage = error.response && error.response.data && typeof error.response.data === 'string'
                       ? error.response.data // If error data is string
                       : error.message; // Default error message
    if (error.response && error.response.data instanceof Blob) {
        try {
            const errText = await error.response.data.text();
            const errJson = JSON.parse(errText);
            if (errJson && errJson.detail) {
                 throw new Error(errJson.detail);
            }
        } catch (e) {
            // Ignore parsing error, use default message
        }
    }
    throw new Error(errorMessage || 'Failed to export CSV file.');
  }
};

export const uploadFeedbackCsv = async (file) => {
  const token = getToken();
  if (!token) {
    console.error('No token found for CSV upload.');
    throw new Error('Authentication token not found. Please login.');
  }

  const formData = new FormData();
  formData.append('csv_file', file); // 'csv_file' must match the FastAPI parameter name in the backend

  const config = {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data', // Axios might set this automatically with FormData, but explicit is fine
    },
  };

  try {
    const response = await axios.post(`${API_URL}/feedback/upload-csv`, formData, config);
    return response.data; // Expects CsvImportResponse: { successful_imports, failed_rows, errors: [...] }
  } catch (error) {
    console.error("Error uploading CSV:", error.response ? error.response.data : error.message);
    // Rethrow a more specific error message if available from backend, otherwise generic
    const errorMessage = error.response && error.response.data && error.response.data.detail
                       ? error.response.data.detail
                       : error.message;
    throw new Error(errorMessage || 'Failed to upload CSV file.');
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
