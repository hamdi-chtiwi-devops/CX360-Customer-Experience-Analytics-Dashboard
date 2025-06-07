import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import FeedbackPage from './pages/FeedbackPage'; // Import FeedbackPage
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/routing/ProtectedRoute'; // Import the actual ProtectedRoute

function App() {
  const { isAuthenticated, logout, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div>Loading application...</div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-blue-600 text-white p-4 shadow-md">
          <ul className="flex space-x-4 items-center container mx-auto">
            <li className="font-bold text-lg"><Link to="/">CX360</Link></li>
            <li className="hover:bg-blue-700 p-2 rounded"><Link to="/">Dashboard</Link></li>
            <li className="hover:bg-blue-700 p-2 rounded"><Link to="/feedback">Feedback</Link></li>
            <li className="flex-grow"></li> {/* Spacer */}
            {isAuthenticated ? (
              <li>
                <button
                  onClick={logout}
                  className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                >
                  Logout
                </button>
              </li>
            ) : (
              <>
                <li className="hover:bg-blue-700 p-2 rounded"><Link to="/login">Login</Link></li>
                <li className="hover:bg-blue-700 p-2 rounded"><Link to="/register">Register</Link></li>
              </>
            )}
          </ul>
        </nav>
        <main className="container mx-auto p-4">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/feedback"
            element={
              <ProtectedRoute>
                <FeedbackPage />
              </ProtectedRoute>
            }
          />
          {/* Add other protected/public routes here */}
        </Routes>
        </main>
      </div>
    </Router>
  );
}
export default App;
