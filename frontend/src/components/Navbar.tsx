import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import uniguru from "../assets/uni-logo.png";
import userimage from "../assets/userimage.png";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useChat } from "../context/ChatContext";
// import { useAuth } from "../context/AuthContext";
import {
  faTimes,
  faBars,
  faSignOutAlt,
  faSignInAlt,
  faHistory,
  faChevronDown,
  faChevronUp,
  faInfoCircle
} from "@fortawesome/free-solid-svg-icons";
import BubblyButton from "./BubblyButton";

const Navbar: React.FC<{
  isLoggedIn: boolean;
  onLogout: () => void;
  isChatStarted: boolean;
}> = ({ isLoggedIn, onLogout, isChatStarted }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { chatSessions, selectChat } = useChat();

  // Dropdown states
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [chatHistoryDropdownOpen, setChatHistoryDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Refs for dropdown management
  const userRef = useRef<HTMLDivElement>(null);
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  const mobileMenuRef = useRef<HTMLDivElement>(null);

  // Toggle functions
  const toggleUserDropdown = () => setUserDropdownOpen(!userDropdownOpen);
  const toggleChatHistoryDropdown = () => setChatHistoryDropdownOpen(!chatHistoryDropdownOpen);
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (userDropdownOpen && userRef.current && !userRef.current.contains(target)) {
        setUserDropdownOpen(false);
      }

      if (chatHistoryDropdownOpen && chatHistoryRef.current && !chatHistoryRef.current.contains(target)) {
        setChatHistoryDropdownOpen(false);
      }

      if (mobileMenuOpen && mobileMenuRef.current && !mobileMenuRef.current.contains(target)) {
        setMobileMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [userDropdownOpen, chatHistoryDropdownOpen, mobileMenuOpen]);

  const isHomePage = location.pathname === "/";
  const isChatPage = location.pathname === "/chatpage";

  // Format chat sessions for display
  const formatChatHistory = () => {
    return chatSessions.slice(0, 10).map(chat => ({
      id: chat.id,
      title: chat.title,
      date: formatDate(chat.lastActivity),
      guru: chat.guru.name,
      messageCount: chat.messageCount
    }));
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return "Today";
    if (diffDays === 2) return "Yesterday";
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };

  const handleChatSelect = (chatId: string) => {
    selectChat(chatId);
    setChatHistoryDropdownOpen(false);
    if (location.pathname !== "/chatpage") {
      navigate("/chatpage");
    }
  };

  const handleNewChat = async () => {
    setChatHistoryDropdownOpen(false);
    navigate("/chatpage");
    // The new chat creation will be handled by the floating button or guru selection
  };

  return (
    <>
      {/* Main Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/30 backdrop-blur-xl border-b border-white/10">
        <div className="w-full px-6">
          <div className="flex items-center justify-between h-16">

            {/* Logo Section - Extreme Left */}
            <div
              className="flex items-center space-x-3 cursor-pointer group"
              onClick={() => navigate("/")}
            >
              <img
                src={uniguru}
                alt="UniGuru Logo"
                className="w-10 h-10 sm:w-12 sm:h-12 object-contain group-hover:scale-105 transition-transform duration-200"
              />
              <h1 className="text-xl sm:text-2xl font-bold bg-clip-text text-transparent"
                  style={{
                    background: "linear-gradient(135deg, #b18615, #d4a01c, #f7c52d, #d4a01c, #b18615)",
                    backgroundClip: "text",
                    WebkitBackgroundClip: "text"
                  }}>
                UniGuru
              </h1>
            </div>

            {/* Desktop Navigation - Center and Right */}
            <div className="hidden md:flex items-center space-x-4 lg:space-x-6 flex-1 justify-center">
              {/* Chat History Dropdown */}
              <div ref={chatHistoryRef} className="relative">
                <button
                  onClick={toggleChatHistoryDropdown}
                  className="flex items-center justify-center space-x-2 px-3 sm:px-5 py-2.5 text-white/80 hover:text-white hover:bg-white/10 transition-all duration-200 font-medium rounded-lg border border-white/10 hover:border-white/20 backdrop-blur-sm touch-target"
                >
                  <FontAwesomeIcon icon={faHistory} className="text-sm" />
                  <span className="hidden lg:inline">Chat History</span>
                  <span className="lg:hidden">History</span>
                  <FontAwesomeIcon
                    icon={chatHistoryDropdownOpen ? faChevronUp : faChevronDown}
                    className="text-xs"
                  />
                </button>
                {chatHistoryDropdownOpen && (
                  <div className="absolute top-full left-0 mt-3 w-80 bg-black/80 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl py-3 z-50">
                    <div className="px-4 py-2 text-xs text-gray-300 border-b border-white/10 font-medium">
                      Recent Conversations
                    </div>
                    {formatChatHistory().length > 0 ? (
                      formatChatHistory().map((chat) => (
                        <button
                          key={chat.id}
                          onClick={() => handleChatSelect(chat.id)}
                          className="w-full px-4 py-3 text-left hover:bg-gray-800 transition-colors group"
                        >
                          <div className="text-sm font-medium text-white truncate group-hover:text-yellow-400">
                            {chat.title}
                          </div>
                          <div className="text-xs text-gray-400 flex justify-between mt-1">
                            <span>{chat.guru} • {chat.messageCount} messages</span>
                            <span>{chat.date}</span>
                          </div>
                        </button>
                      ))
                    ) : (
                      <div className="px-4 py-3 text-sm text-gray-400 text-center">
                        No chat history yet
                      </div>
                    )}
                    <div className="border-t border-gray-700 mt-2 pt-2">
                      <button
                        onClick={handleNewChat}
                        className="w-full px-4 py-2 text-left text-yellow-400 hover:bg-gray-800 transition-colors text-sm font-medium"
                      >
                        + Start New Chat
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* About Link */}
              <button
                onClick={() => navigate("/about")}
                className="flex items-center space-x-2 px-4 py-2 text-white hover:text-yellow-400 transition-colors font-medium"
              >
                <FontAwesomeIcon icon={faInfoCircle} className="text-sm" />
                <span>About</span>
              </button>
            </div>

            {/* Desktop Auth Section - Extreme Right */}
            <div className="hidden md:flex items-center space-x-4">
              {/* Homepage Auth Buttons */}
              {isHomePage && !isLoggedIn && !isChatStarted && (
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => navigate("/login")}
                    className="flex items-center justify-center px-5 py-2.5 text-white/80 hover:text-white hover:bg-white/10 transition-all duration-200 font-medium rounded-lg border border-white/10 hover:border-white/20 backdrop-blur-sm"
                  >
                    Login
                  </button>
                  <BubblyButton
                    onClick={() => navigate("/signup")}
                    variant="secondary"
                    className="px-6 py-2.5 font-medium text-sm flex items-center justify-center"
                  >
                    Sign Up
                  </BubblyButton>
                </div>
              )}

              {/* Chat Page - Only keep essential navbar items */}
              {isChatPage && (
                <>

                  {/* User Authentication Section */}
                  {isLoggedIn ? (
                    <div ref={userRef} className="relative">
                      <button
                        onClick={toggleUserDropdown}
                        className="flex items-center space-x-2 p-1 rounded-full hover:bg-gray-800/50 transition-colors"
                      >
                        <img
                          src={userimage}
                          alt="User Avatar"
                          className="w-8 h-8 rounded-full object-cover border-2 border-gray-600"
                        />
                      </button>
                      {userDropdownOpen && (
                        <div className="absolute top-full right-0 mt-2 w-48 bg-gray-900/95 backdrop-blur-sm border border-gray-700 rounded-lg shadow-xl py-2">
                          <button
                            onClick={onLogout}
                            className="w-full px-4 py-2 text-left text-red-400 hover:bg-gray-800 transition-colors flex items-center space-x-2"
                          >
                            <FontAwesomeIcon icon={faSignOutAlt} className="text-sm" />
                            <span>Logout</span>
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <button
                      onClick={() => navigate("/login")}
                      className="flex items-center justify-center space-x-2 px-5 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all duration-200 border border-white/20 hover:border-white/30 backdrop-blur-sm font-medium"
                    >
                      <FontAwesomeIcon icon={faSignInAlt} className="text-sm" />
                      <span className="text-sm">Login</span>
                    </button>
                  )}
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button
                onClick={toggleMobileMenu}
                className="p-2.5 text-gray-300 hover:text-white transition-colors touch-target rounded-lg hover:bg-white/10"
              >
                <FontAwesomeIcon icon={mobileMenuOpen ? faTimes : faBars} className="text-lg" />
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div ref={mobileMenuRef} className="md:hidden bg-gray-900/95 backdrop-blur-sm border-t border-gray-700 animate-mobile-slide-down mobile-safe-area">
            <div className="px-4 py-4 space-y-3 mobile-scroll max-h-[calc(100vh-4rem)] overflow-y-auto">

              {/* Mobile Navigation Links */}
              <div className="space-y-2 border-b border-gray-700 pb-3 mb-3">
                {/* Chat History Mobile */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-gray-400 px-2">Chat History</div>
                  {formatChatHistory().slice(0, 3).length > 0 ? (
                    formatChatHistory().slice(0, 3).map((chat) => (
                      <button
                        key={chat.id}
                        onClick={() => {
                          handleChatSelect(chat.id);
                          setMobileMenuOpen(false);
                        }}
                        className="w-full px-4 py-3 text-white hover:bg-gray-800 rounded-lg transition-colors text-left touch-target"
                      >
                        <div className="text-sm font-medium truncate">{chat.title}</div>
                        <div className="text-xs text-gray-400">{chat.guru} • {chat.date}</div>
                      </button>
                    ))
                  ) : (
                    <div className="px-4 py-3 text-sm text-gray-400 text-center">
                      No chat history yet
                    </div>
                  )}
                  <button
                    onClick={() => {
                      handleNewChat();
                      setMobileMenuOpen(false);
                    }}
                    className="w-full px-4 py-2 text-yellow-400 hover:bg-gray-800 rounded-lg transition-colors text-left text-sm font-medium"
                  >
                    + Start New Chat
                  </button>
                </div>

                {/* About Mobile */}
                <button
                  onClick={() => {
                    navigate("/about");
                    setMobileMenuOpen(false);
                  }}
                  className="w-full px-4 py-2 text-white hover:bg-gray-800 rounded-lg transition-colors text-left flex items-center space-x-2"
                >
                  <FontAwesomeIcon icon={faInfoCircle} className="text-sm" />
                  <span>About</span>
                </button>
              </div>

              {/* Homepage Mobile Auth */}
              {isHomePage && !isLoggedIn && !isChatStarted && (
                <div className="space-y-2">
                  <button
                    onClick={() => {
                      navigate("/login");
                      setMobileMenuOpen(false);
                    }}
                    className="w-full px-4 py-2 text-white hover:bg-gray-800 rounded-lg transition-colors text-left"
                  >
                    Login
                  </button>
                  <BubblyButton
                    onClick={() => {
                      navigate("/signup");
                      setMobileMenuOpen(false);
                    }}
                    variant="secondary"
                    className="w-full px-4 py-2 font-medium rounded-lg"
                  >
                    Sign Up
                  </BubblyButton>
                </div>
              )}

              {/* Chat Page Mobile - Only keep essential items */}
              {isChatPage && (
                <div className="space-y-2">

                  {/* Mobile Authentication Section */}
                  {isLoggedIn ? (
                    <button
                      onClick={() => {
                        onLogout();
                        setMobileMenuOpen(false);
                      }}
                      className="w-full px-4 py-2 text-red-400 hover:bg-gray-800 rounded-lg transition-colors text-left flex items-center space-x-2"
                    >
                      <FontAwesomeIcon icon={faSignOutAlt} className="text-sm" />
                      <span>Logout</span>
                    </button>
                  ) : (
                    <button
                      onClick={() => {
                        navigate("/login");
                        setMobileMenuOpen(false);
                      }}
                      className="w-full px-4 py-2 text-white hover:bg-gray-800 rounded-lg transition-colors text-left flex items-center space-x-2"
                    >
                      <FontAwesomeIcon icon={faSignInAlt} className="text-sm" />
                      <span>Login</span>
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </nav>
    </>
  );
};

export default Navbar;