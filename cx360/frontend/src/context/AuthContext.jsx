import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentUser as fetchCurrentUser } from '../services/authService'; // Renamed to avoid conflict

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true); // For initial loading state

  useEffect(() => {
    const loadUserFromToken = async () => {
      setIsLoading(true);
      if (token) {
        localStorage.setItem('token', token); // Ensure token is in localStorage
        try {
          const userData = await fetchCurrentUser(); // Fetches user based on token in localStorage
          if (userData) {
            setUser(userData);
            setIsAuthenticated(true);
          } else {
            // Token might be invalid or expired
            localStorage.removeItem('token');
            setToken(null);
            setUser(null);
            setIsAuthenticated(false);
          }
        } catch (error) {
          console.error("Failed to load user from token:", error);
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
          setIsAuthenticated(false);
        }
      } else {
        // No token, ensure logged out state
        localStorage.removeItem('token'); // Clean up just in case
        setToken(null);
        setUser(null);
        setIsAuthenticated(false);
      }
      setIsLoading(false);
    };

    loadUserFromToken();
  }, [token]); // Re-run when token changes (e.g. after login) or on initial load

  const login = (newToken, userData) => {
    localStorage.setItem('token', newToken);
    setToken(newToken); // This will trigger the useEffect to load user
    setUser(userData); // Optionally set user data immediately if available from login response
    setIsAuthenticated(true);
    // If userData is not passed, useEffect will fetch it.
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  // loadUser function can be used if we need to manually refresh user data
  // For now, useEffect handles loading on token change.

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
