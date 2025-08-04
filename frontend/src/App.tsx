import React, { useState, useEffect } from "react";
import { Route, Routes, useNavigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Navbar from "./components/Navbar";
import HomePage from "./routes/HomePage";
import LoginPage from "./routes/LoginPage";
import SignupPage from "./routes/SignupPage";
import ForgotPasswordPage from "./routes/ForgotPasswordPage";
import ResetPasswordPage from "./routes/ResetPasswordPage";
import ToolsPage from "./routes/ToolsPage";
import AboutPage from "./routes/AboutPage";
import NotFoundPage from "./routes/NotFoundPage";

import StarsCanvas from "./components/StarBackground";
import ChatPage from "./routes/ChatPage";
import BubblyButtonDemo from "./components/BubblyButtonDemo";
import AppInitializer from "./components/AppInitializer";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isChatStarted, setIsChatStarted] = useState(false); // Track if Let's Chat was clicked
  const navigate = useNavigate();

  useEffect(() => {
    const loggedInState = localStorage.getItem("isLoggedIn") === "true";
    setIsLoggedIn(loggedInState);
  }, []);



  const handleLogout = () => {
    setIsLoggedIn(false);
    localStorage.removeItem("isLoggedIn");
    navigate("/");
  };

  const handleChatStarted = () => {
    setIsChatStarted(true); // Hide Login/Signup buttons when Let's Chat is clicked
  };

  return (
    <main>
      <AppInitializer>
        <Routes>
        <Route
          path="/"
          element={
            <>
              <Navbar
                isLoggedIn={isLoggedIn}
                onLogout={handleLogout}
                isChatStarted={isChatStarted}
              />
              <div className="absolute inset-0 -z-10">
                <StarsCanvas />
              </div>
              <HomePage
                onChatStarted={handleChatStarted}
              />
            </>
          }
        />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route
          path="/tools"
          element={
            <>
              <Navbar
                isLoggedIn={isLoggedIn}
                onLogout={handleLogout}
                isChatStarted={isChatStarted}
              />
              <div className="absolute inset-0 -z-10">
                <StarsCanvas />
              </div>
              <ToolsPage />
            </>
          }
        />
        <Route
          path="/chatpage"
          element={
            <>
              <Navbar
                isLoggedIn={isLoggedIn}
                onLogout={handleLogout}
                isChatStarted={isChatStarted}
              />
              <div className="absolute inset-0 -z-10">
                <StarsCanvas />
              </div>
              <ChatPage />
            </>
          }
        />
        <Route
          path="/about"
          element={
            <>
              <Navbar
                isLoggedIn={isLoggedIn}
                onLogout={handleLogout}
                isChatStarted={isChatStarted}
              />
              <div className="absolute inset-0 -z-10">
                <StarsCanvas />
              </div>
              <AboutPage />
            </>
          }
        />
        <Route path="/demo" element={<BubblyButtonDemo />} />

        {/* 404 NotFound - Catch all unmatched routes */}
        <Route
          path="*"
          element={
            <>
              <div className="absolute inset-0 -z-10">
                <StarsCanvas />
              </div>
              <NotFoundPage />
            </>
          }
        />
      </Routes>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1f2937',
            color: '#f9fafb',
            border: '1px solid #374151',
            borderRadius: '8px',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#f9fafb',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#f9fafb',
            },
          },
        }}
      />
      </AppInitializer>
    </main>
  );
}

export default App;
