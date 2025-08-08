import React from "react";
import { useNavigate, Link } from "react-router-dom";
import Loginbox from "../components/Loginbox";
import StarsCanvas from "../components/StarBackground";

const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  const handleLoginSuccess = () => {
    // AuthContext will handle the login state, no need for localStorage
    navigate("/chatpage", { replace: true });
  };

  return (
    <div className="relative">
      {/* Star Background */}
      <div className="fixed inset-0 z-0">
        <StarsCanvas />
      </div>

      {/* Login Container */}
      <div className="relative z-10">
        <Loginbox onLoginSuccess={handleLoginSuccess} />
      </div>

      {/* Additional Links */}
      <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 text-center space-y-2 z-20">
        <div className="text-white text-sm font-poppins space-y-1">
          <p>
            Don't have an account?{" "}
            <Link
              to="/signup"
              className="text-blue-300 hover:text-blue-200 underline transition-colors duration-200"
            >
              Sign up here
            </Link>
          </p>
          <p>
            <Link
              to="/forgot-password"
              className="text-blue-300 hover:text-blue-200 underline transition-colors duration-200"
            >
              Forgot your password?
            </Link>
          </p>
          <p>
            <Link
              to="/"
              className="text-white/70 hover:text-white underline transition-colors duration-200"
            >
              Back to Home
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
