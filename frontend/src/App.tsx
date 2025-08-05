import { useState, useEffect } from "react";
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
import { useGuru } from "./context/GuruContext";
import { useChat } from "./context/ChatContext";
import toast from "react-hot-toast";

// Wrapper component for ChatPage that handles chat creation
const ChatPageWrapper: React.FC<{
  isLoggedIn: boolean;
  onLogout: () => void;
  isChatStarted: boolean;
}> = ({ isLoggedIn, onLogout, isChatStarted }) => {
  const { selectedGuru } = useGuru();
  const { createNewChatManually } = useChat();
  const [isCreatingChat, setIsCreatingChat] = useState(false);

  const handleCreateNewChat = async () => {
    if (!selectedGuru) {
      toast.error("Please select a guru first", {
        icon: '🧙‍♂️'
      });
      return;
    }

    setIsCreatingChat(true);
    toast.loading("Creating new chat...", { id: "create-chat-main" });

    try {
      await createNewChatManually(selectedGuru.id);
      toast.success("New chat created! 🎉", {
        id: "create-chat-main",
        icon: '💬'
      });
    } catch (error) {
      console.error("Error creating new chat:", error);
      toast.error("Failed to create new chat. Please try again.", { id: "create-chat-main" });
    } finally {
      setIsCreatingChat(false);
    }
  };

  return (
    <div className="relative h-screen overflow-hidden">
      <div className="fixed inset-0 z-0">
        <StarsCanvas />
      </div>
      <Navbar
        isLoggedIn={isLoggedIn}
        onLogout={onLogout}
        isChatStarted={isChatStarted}
        onCreateNewChat={handleCreateNewChat}
        isCreatingChat={isCreatingChat}
      />
      <ChatPage
        onCreateNewChat={handleCreateNewChat}
        isCreatingChat={isCreatingChat}
      />
    </div>
  );
};

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
    <div className="min-h-screen bg-black">
      <AppInitializer>
        <Routes>
        <Route
          path="/"
          element={
            <div className="relative min-h-screen">
              <div className="fixed inset-0 z-0">
                <StarsCanvas />
              </div>
              <Navbar
                isLoggedIn={isLoggedIn}
                onLogout={handleLogout}
                isChatStarted={isChatStarted}
              />
              <HomePage
                onChatStarted={handleChatStarted}
              />
            </div>
          }
        />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route
          path="/tools"
          element={
            <div className="relative min-h-screen">
              <div className="fixed inset-0 z-0">
                <StarsCanvas />
              </div>
              <Navbar
                isLoggedIn={isLoggedIn}
                onLogout={handleLogout}
                isChatStarted={isChatStarted}
              />
              <div className="pt-16">
                <ToolsPage />
              </div>
            </div>
          }
        />
        <Route
          path="/chatpage"
          element={
            <ChatPageWrapper
              isLoggedIn={isLoggedIn}
              onLogout={handleLogout}
              isChatStarted={isChatStarted}
            />
          }
        />
        <Route
          path="/about"
          element={
            <div className="relative min-h-screen">
              <div className="fixed inset-0 z-0">
                <StarsCanvas />
              </div>
              <Navbar
                isLoggedIn={isLoggedIn}
                onLogout={handleLogout}
                isChatStarted={isChatStarted}
              />
              <div className="pt-16">
                <AboutPage />
              </div>
            </div>
          }
        />
        <Route path="/demo" element={<BubblyButtonDemo />} />

        {/* 404 NotFound - Catch all unmatched routes */}
        <Route
          path="*"
          element={
            <div className="relative min-h-screen">
              <div className="fixed inset-0 z-0">
                <StarsCanvas />
              </div>
              <NotFoundPage />
            </div>
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
    </div>
  );
}

export default App;
