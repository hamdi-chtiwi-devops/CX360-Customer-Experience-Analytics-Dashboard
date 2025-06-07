import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import RegisterForm from '../../components/auth/RegisterForm';
import { registerUser } from '../../services/authService';
// import { useAuth } from '../../context/AuthContext'; // Not typically used directly on registration success

function RegisterPage() {
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();
  // const { login } = useAuth(); // If auto-login after register

  const handleRegister = async (userData) => {
    try {
      setError('');
      setSuccessMessage('');
      // Add default role if not provided by form, or handle in backend
      // const dataToSend = { ...userData, role: userData.role || 'agent' };
      await registerUser(userData);
      setSuccessMessage('Registration successful! Please login.');
      // Optionally, redirect to login page after a short delay
      setTimeout(() => {
        navigate('/login');
      }, 2000); // 2 seconds delay
    } catch (err) {
      console.error('Registration error:', err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to register. Please try again.');
      }
      setSuccessMessage('');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 p-10 bg-white shadow-lg rounded-xl">
        {/* <h1>Register Page</h1> // Title is now inside RegisterForm */}
        {successMessage && <p className="text-green-600 text-center mb-4">{successMessage}</p>}
        <RegisterForm onRegister={handleRegister} error={error} />
      </div>
    </div>
  );
}
export default RegisterPage;
