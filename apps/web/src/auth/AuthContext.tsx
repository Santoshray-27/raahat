import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthUser {
  uid: string;
  email?: string;
  displayName: string;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  loginDevMode: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  loginDevMode: () => {},
  logout: () => {}
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>({
    uid: 'dev_user_999',
    displayName: 'Santosh Ray (Dev User)'
  });
  const [token, setToken] = useState<string | null>('dev_token_bypass');

  const loginDevMode = () => {
    setUser({ uid: 'dev_user_999', displayName: 'Santosh Ray' });
    setToken('dev_token_bypass');
    localStorage.setItem('raahat_auth_token', 'dev_token_bypass');
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('raahat_auth_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, loginDevMode, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
