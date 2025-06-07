import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Assuming backend is on port 8000

// Note: FastAPI backend uses username and password in a FormData for /auth/token
// and UserCreate model (JSON) for /auth/register.

export const loginUser = async (credentials) => {
  // FastAPI's OAuth2PasswordRequestForm expects 'username' and 'password' as form data
  const formData = new FormData();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const response = await axios.post(`${API_URL}/auth/token`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  // Token is typically stored by the caller (e.g., AuthContext or page) after successful call
  // For example: if (response.data.access_token) { localStorage.setItem('token', response.data.access_token); }
  return response.data; // { access_token: "...", token_type: "bearer" }
};

export const registerUser = async (userData) => {
  // userData: { username, email, password, role (optional) }
  const response = await axios.post(`${API_URL}/auth/register`, userData);
  return response.data; // UserResponse model
};

export const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    // console.log("No token found in localStorage");
    return null;
  }

  // console.log("Token found, attempting to fetch current user:", token);
  try {
    const response = await axios.get(`${API_URL}/auth/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    // console.log("Get current user response:", response.data);
    return response.data; // UserResponse model
  } catch (error) {
    // console.error("Error fetching current user:", error.response ? error.response.data : error.message);
    // It's common for this to fail if token is expired or invalid
    // localStorage.removeItem('token'); // Optionally remove bad token
    return null;
  }
};
