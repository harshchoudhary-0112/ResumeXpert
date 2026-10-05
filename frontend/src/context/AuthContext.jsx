/**
 * Authentication context — manages JWT token, user state,
 * and login/logout/register flows.
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('resumexpert_token'));
  const [loading, setLoading] = useState(true);

  // Load user profile if we have a token
  const loadUser = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const res = await authAPI.getProfile();
      setUser(res.data);
    } catch {
      // Token invalid/expired
      localStorage.removeItem('resumexpert_token');
      localStorage.removeItem('resumexpert_user');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (email, password) => {
    const res = await authAPI.login({ email, password });
    const { access_token } = res.data;
    localStorage.setItem('resumexpert_token', access_token);
    setToken(access_token);

    // Fetch user profile
    const profileRes = await authAPI.getProfile();
    setUser(profileRes.data);
    localStorage.setItem('resumexpert_user', JSON.stringify(profileRes.data));
    return profileRes.data;
  };

  const register = async (name, email, password, confirm_password) => {
    // Step 1 only — sends OTP. Login happens after OTP verification.
    const res = await authAPI.register({ name, email, password, confirm_password });
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('resumexpert_token');
    localStorage.removeItem('resumexpert_user');
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    login,
    register,
    logout,
    refreshUser: loadUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
