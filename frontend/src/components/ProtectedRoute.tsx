import React from "react";
import { Navigate } from "react-router-dom";
import LoadingSpinner from "./LoadingSpinner";
import StarsCanvas from "./StarBackground";
import { useAuth } from "../context/AuthContext";

interface ProtectedRouteProps {
  children: React.ReactNode;
  isLoggedIn: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, isLoggedIn }) => {
  const { isAuthLoading } = useAuth();

  // Show loading screen while checking authentication
  if (isAuthLoading) {
    return (
      <div className="relative min-h-screen bg-black">
        <div className="fixed inset-0 z-0">
          <StarsCanvas />
        </div>
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <div className="bg-glass-card backdrop-blur-xl rounded-xl p-8 border border-glass-border shadow-glass">
            <LoadingSpinner
              size="large"
              variant="gradient-ring"
              text="Verifying authentication..."
            />
          </div>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
