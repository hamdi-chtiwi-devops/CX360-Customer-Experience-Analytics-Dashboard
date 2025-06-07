import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../../components/auth/LoginForm';
import { loginUser } from '../../services/authService';
import { useAuth } from '../../context/AuthContext';

function LoginPage() {
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (credentials) => {
    try {
      setError('');
      const data = await loginUser(credentials); // data should contain { access_token, token_type }
      if (data.access_token) {
        // The authService.loginUser itself doesn't store the token in localStorage
        // The AuthContext's login function will handle storing token and user state
        login(data.access_token); // AuthContext handles localStorage and user fetching
        navigate('/'); // Redirect to dashboard or home page
      } else {
        setError('Login failed: No access token received.');
      }
    } catch (err) {
      console.error('Login error:', err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to login. Please check your credentials or server status.');
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 p-10 bg-white shadow-lg rounded-xl">
        {/* <h1>Login Page</h1> // Title is now inside LoginForm */}
        <LoginForm onLogin={handleLogin} error={error} />
      </div>
    </div>
  );
}
export default LoginPage;
