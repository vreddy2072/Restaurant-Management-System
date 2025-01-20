import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'staff' | 'customer';  // Keeping the interface but not using it
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children 
}) => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  console.log('ProtectedRoute - Auth status:', { isAuthenticated, location });

  if (!isAuthenticated) {
    // Redirect to the login page with the return url
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  // Removed role check - all authenticated users can access
  return <>{children}</>;
};

export default ProtectedRoute;
