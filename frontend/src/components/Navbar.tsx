import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import uniguru from "../assets/uni-logo.png";
import userimage from "../assets/userimage.png";
import guruLogo from "../assets/guru.png";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import { useAuth } from "../context/AuthContext";
import {
  faTimes,
  faBars,
  faSignOutAlt,
  faSignInAlt,
  faInfoCircle,
  faRefresh,
  faTrash,
  faEdit,
  faUserPlus,

} from "@fortawesome/free-solid-svg-icons";
import BubblyButton from "./BubblyButton";
import { useGuru } from "../context/GuruContext";
import { useChat } from "../context/ChatContext";
import { useAuth } from "../context/AuthContext";
import { createCustomGuru } from "../helpers/api-communicator";
import toast from "react-hot-toast";

interface NavbarProps {
  onLogout: () => void;
  isChatStarted: boolean;
  onCreateNewChat?: () => void;
  isCreatingChat?: boolean;
}

const Navbar: React.FC<NavbarProps> = ({
  onLogout,
  isChatStarted,
  onCreateNewChat,
  isCreatingChat
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isLoggedIn } = useAuth();
  const { gurus, addGuru, removeGuru, selectedGuru, refreshGurus, selectGuru } = useGuru();
  const { getChatsByGuru, selectChat, currentChatId, deleteChat, renameChat } = useChat();

  // Dropdown states
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Mobile sidebar states (only used on mobile)
  const [activeSection, setActiveSection] = useState<'gurus' | 'chats'>('gurus');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [, ] = useState<string | null>(null);
  const [editingChat, setEditingChat] = useState<string | null>(null);
  const [editingChatName, setEditingChatName] = useState('');

  // Form states for guru creation
  const [guruFormData, setGuruFormData] = useState({
    name: '',
    subject: '',
    description: ''
  });

  // Confirmation modal states
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{
    type: 'deleteGuru' | 'deleteChat';
    id: string;
    name: string;
    action: () => void;
  } | null>(null);

  // Refs for dropdown management
  const userRef = useRef<HTMLDivElement>(null);
  const mobileMenuRef = useRef<HTMLDivElement>(null);
  const mobileMenuButtonRef = useRef<HTMLButtonElement>(null);

  // Handle guru creation
  const handleCreateGuru = async () => {
    if (!user || !guruFormData.name.trim() || !guruFormData.subject.trim()) {
      toast.error("Please fill in name and subject", {
        icon: '⚠️'
      });
      return;
    }

    toast.loading("Creating guru...", { id: "create-guru" });

    try {
      const newGuruResponse = await createCustomGuru(
        user.id,
        guruFormData.name.trim(),
        guruFormData.subject.trim(),
        guruFormData.description.trim()
      );

      const newGuru = {
        id: newGuruResponse.chatbot?._id || newGuruResponse.guru?.id || newGuruResponse.id,
        name: newGuruResponse.chatbot?.name || guruFormData.name.trim(),
        subject: newGuruResponse.chatbot?.subject || guruFormData.subject.trim(),
        description: newGuruResponse.chatbot?.description || guruFormData.description.trim(),
        userid: user.id
      };

      addGuru(newGuru);
      setGuruFormData({ name: '', subject: '', description: '' });
      setShowCreateForm(false);

      toast.success("Guru created successfully!", {
        id: "create-guru",
        icon: '🎉'
      });
    } catch (error) {
      console.error('Error creating guru:', error);
      toast.error("Failed to create guru. Please try again.", {
        id: "create-guru",
        icon: '❌'
      });
    }
  };

  // Toggle functions
  const toggleUserDropdown = () => setUserDropdownOpen(!userDropdownOpen);

  // Confirmation modal functions
  const showDeleteConfirmation = (type: 'deleteGuru' | 'deleteChat', id: string, name: string, action: () => void) => {
    setConfirmAction({ type, id, name, action });
    setShowConfirmModal(true);
  };

  const handleConfirmDelete = () => {
    if (confirmAction) {
      confirmAction.action();
    }
    setShowConfirmModal(false);
    setConfirmAction(null);
  };

  const handleCancelDelete = () => {
    setShowConfirmModal(false);
    setConfirmAction(null);
  };

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      const target = event.target as Node;

      // Close user dropdown if clicking outside
      if (userDropdownOpen && userRef.current && !userRef.current.contains(target)) {
        setUserDropdownOpen(false);
      }

      // Close mobile menu if clicking outside the menu area AND not on the toggle button
      if (mobileMenuOpen && mobileMenuRef.current && !mobileMenuRef.current.contains(target)) {
        // Check if the click is on the mobile menu button or its children
        if (mobileMenuButtonRef.current && !mobileMenuButtonRef.current.contains(target)) {
          setMobileMenuOpen(false);
        }
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("touchstart", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
    };
  }, [userDropdownOpen, mobileMenuOpen]);

  // Listen for Create Guru trigger from chat area (mobile)
  useEffect(() => {
    const onOpenGuruCreate = (_e: Event) => {
      if (location.pathname === "/chatpage") {
        setMobileMenuOpen(true);
        setActiveSection('gurus');
        setShowCreateForm(true);
      }
    };
    window.addEventListener('open-guru-create' as any, onOpenGuruCreate as EventListener);
    return () => {
      window.removeEventListener('open-guru-create' as any, onOpenGuruCreate as EventListener);
    };
  }, [location.pathname]);

  const isHomePage = location.pathname === "/";
  const isChatPage = location.pathname === "/chatpage";

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

            {/* Desktop Auth Section - Extreme Right */}
            <div className="hidden md:flex items-center space-x-4">
              {/* About Link */}
              <button
                onClick={() => navigate("/about")}
                className="flex items-center space-x-2 px-4 py-2 text-white hover:text-yellow-400 transition-colors font-medium"
              >
                <FontAwesomeIcon icon={faInfoCircle} className="text-sm" />
                <span>About</span>
              </button>
              {/* Homepage Auth Buttons */}
              {isHomePage && !isLoggedIn && !isChatStarted && (
                <div className="flex items-center space-x-3">
                  <BubblyButton
                    onClick={() => navigate("/login")}
                    variant="primary"
                    className="px-6 py-2.5 font-medium text-sm flex items-center justify-center"
                  >
                    Login
                  </BubblyButton>
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
                    <BubblyButton
                      onClick={() => navigate("/login")}
                      variant="primary"
                      className="flex items-center justify-center space-x-2 px-5 py-2.5 font-medium text-sm"
                    >
                      <FontAwesomeIcon icon={faSignInAlt} className="text-sm" />
                      <span>Login</span>
                    </BubblyButton>
                  )}
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden relative z-50">
              <button
                ref={mobileMenuButtonRef}
                onClick={(e) => {
                  e.stopPropagation();
                  setMobileMenuOpen(!mobileMenuOpen);
                }}
                className={`p-3 transition-all duration-300 touch-target rounded-xl relative z-50 min-w-[48px] min-h-[48px] flex items-center justify-center border ${
                  mobileMenuOpen
                    ? 'text-white bg-gradient-to-br from-purple-600 to-blue-600 border-purple-500/50 shadow-lg shadow-purple-500/25'
                    : 'text-gray-300 hover:text-white hover:bg-gradient-to-br hover:from-purple-600/20 hover:to-blue-600/20 border-transparent hover:border-purple-500/30'
                }`}
                aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
                type="button"
                style={{ touchAction: 'manipulation', userSelect: 'none' }}
              >
                <FontAwesomeIcon
                  icon={mobileMenuOpen ? faTimes : faBars}
                  className={`text-lg pointer-events-none transition-transform duration-300 ${
                    mobileMenuOpen ? 'rotate-90' : 'rotate-0'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div ref={mobileMenuRef} className="md:hidden animate-mobile-slide-down mobile-menu-safe-area">
            <div className="px-6 py-3 space-y-3 mobile-scroll max-h-[calc(100vh-5rem)] overflow-y-auto">



              {/* Chat Page Mobile - Include sidebar content */}
              {isChatPage && (
                <div className="space-y-4">
                  {/* Sidebar Navigation Tabs */}
                  <div className="flex border-b border-gray-700 mb-4">
                    <button
                      onClick={() => setActiveSection('gurus')}
                      className={`flex-1 py-3 px-4 text-sm font-medium transition-all duration-200 flex items-center justify-center ${
                        activeSection === 'gurus'
                          ? 'text-purple-300 border-b-2 border-purple-400 bg-purple-400/10'
                          : 'text-gray-300 hover:text-purple-300 hover:bg-purple-400/5'
                      }`}
                    >
                      <img src={guruLogo} alt="Guru" className="w-4 h-4 mr-2" />
                      Gurus
                    </button>
                    <button
                      onClick={() => setActiveSection('chats')}
                      className={`flex-1 py-3 px-4 text-sm font-medium transition-all duration-200 ${
                        activeSection === 'chats'
                          ? 'text-purple-300 border-b-2 border-purple-400 bg-purple-400/10'
                          : 'text-gray-300 hover:text-purple-300 hover:bg-purple-400/5'
                      }`}
                    >
                      <FontAwesomeIcon icon={faBars} className="mr-2 text-sm" />
                      Chats
                    </button>
                  </div>

                  {/* Gurus Section */}
                  {activeSection === 'gurus' && (
                    <div className="space-y-3">
                      {/* Action Buttons */}
                      <div className="flex gap-2">
                        <BubblyButton
                          onClick={() => setShowCreateForm(!showCreateForm)}
                          variant="primary"
                          className="flex-1 flex items-center justify-center gap-2 py-2 px-3 font-medium text-sm"
                        >

                          <span>Create Guru</span>
                        </BubblyButton>
                        <button
                          onClick={() => {
                            setIsRefreshing(true);
                            refreshGurus().finally(() => setIsRefreshing(false));
                          }}
                          disabled={isRefreshing}
                          className="text-purple-300 hover:text-white transition-all duration-200 p-2 rounded-full hover:bg-purple-400/10 disabled:opacity-50"
                          title="Refresh Gurus"
                        >
                          <FontAwesomeIcon icon={faRefresh} className={`text-sm ${isRefreshing ? 'animate-spin' : ''}`} />
                        </button>
                      </div>

                      {/* Create Guru Form */}
                      {showCreateForm && (
                        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                          <h3 className="text-white font-medium mb-3 text-sm">Create New Guru</h3>
                          {/* Form content would go here - simplified for mobile */}
                          <div className="space-y-2">
                            <input
                              type="text"
                              placeholder="Guru Name"
                              value={guruFormData.name}
                              onChange={(e) => setGuruFormData(prev => ({ ...prev, name: e.target.value }))}
                              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg text-sm border border-gray-600 focus:border-purple-400 focus:outline-none"
                            />
                            <input
                              type="text"
                              placeholder="Subject"
                              value={guruFormData.subject}
                              onChange={(e) => setGuruFormData(prev => ({ ...prev, subject: e.target.value }))}
                              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg text-sm border border-gray-600 focus:border-purple-400 focus:outline-none"
                            />
                            <textarea
                              placeholder="Description"
                              rows={3}
                              value={guruFormData.description}
                              onChange={(e) => setGuruFormData(prev => ({ ...prev, description: e.target.value }))}
                              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg text-sm border border-gray-600 focus:border-purple-400 focus:outline-none resize-none"
                            />
                            <div className="flex gap-2 pt-2">
                              <BubblyButton
                                onClick={handleCreateGuru}
                                variant="primary"
                                className="flex-1 py-2 text-sm"
                                disabled={!guruFormData.name.trim() || !guruFormData.subject.trim()}
                              >
                                Create
                              </BubblyButton>
                              <button
                                onClick={() => {
                                  setShowCreateForm(false);
                                  setGuruFormData({ name: '', subject: '', description: '' });
                                }}
                                className="flex-1 py-2 text-sm bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors"
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Gurus List */}
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {gurus.map((guru) => (
                          <div
                            key={guru.id}
                            onClick={() => {
                              selectGuru(guru);
                              setMobileMenuOpen(false);
                            }}
                            className={`p-3 rounded-lg cursor-pointer transition-all duration-200 border ${
                              selectedGuru?.id === guru.id
                                ? 'bg-purple-400/20 border-purple-400/40 text-purple-200'
                                : 'bg-gray-800/30 border-gray-700/50 text-gray-300 hover:bg-gray-700/50 hover:border-gray-600/50'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1 min-w-0">
                                <h4 className="font-medium text-sm truncate">{guru.name}</h4>
                                <p className="text-xs opacity-75 truncate">{guru.subject}</p>
                              </div>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  showDeleteConfirmation('deleteGuru', guru.id, guru.name, () => removeGuru(guru.id));
                                }}
                                className="ml-2 text-red-400 hover:text-red-300 transition-colors p-1"
                              >
                                <FontAwesomeIcon icon={faTrash} className="text-xs" />
                              </button>
                            </div>
                          </div>
                        ))}
                        {gurus.length === 0 && (
                          <div className="text-center py-6 text-gray-400">
                            <img src={guruLogo} alt="Guru" className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p className="text-sm">No gurus yet</p>
                            <p className="text-xs">Create your first guru!</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Chats Section */}
                  {activeSection === 'chats' && (
                    <div className="space-y-3">
                      {/* New Chat Button */}
                      {selectedGuru && onCreateNewChat && (
                        <BubblyButton
                          onClick={() => {
                            onCreateNewChat();
                            setMobileMenuOpen(false);
                          }}
                          variant="primary"
                          disabled={isCreatingChat}
                          className="w-full flex items-center justify-center gap-2 py-2 px-3 font-medium text-sm"
                        >

                          <span>{isCreatingChat ? 'Creating...' : 'New Chat'}</span>
                        </BubblyButton>
                      )}

                      {/* Chats List */}
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {selectedGuru ? (
                          getChatsByGuru(selectedGuru.id).map((chat) => (
                            <div
                              key={chat.id}
                              className={`p-3 rounded-lg cursor-pointer transition-all duration-200 border ${
                                currentChatId === chat.id
                                  ? 'bg-purple-400/20 border-purple-400/40 text-purple-200'
                                  : 'bg-gray-800/30 border-gray-700/50 text-gray-300 hover:bg-gray-700/50'
                              }`}
                            >
                              <div className="flex items-center justify-between">
                                <div
                                  className="flex-1 min-w-0"
                                  onClick={() => {
                                    selectChat(chat.id);
                                    setMobileMenuOpen(false);
                                  }}
                                >
                                  {editingChat === chat.id ? (
                                    <input
                                      type="text"
                                      value={editingChatName}
                                      onChange={(e) => setEditingChatName(e.target.value)}
                                      onBlur={() => {
                                        if (editingChatName.trim()) {
                                          renameChat(chat.id, editingChatName.trim());
                                        }
                                        setEditingChat(null);
                                      }}
                                      onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                          if (editingChatName.trim()) {
                                            renameChat(chat.id, editingChatName.trim());
                                          }
                                          setEditingChat(null);
                                        } else if (e.key === 'Escape') {
                                          setEditingChat(null);
                                        }
                                      }}
                                      className="w-full bg-gray-700 text-white px-2 py-1 rounded text-sm"
                                      autoFocus
                                    />
                                  ) : (
                                    <>
                                      <h4 className="font-medium text-sm truncate">{chat.title}</h4>
                                      <p className="text-xs opacity-75">
                                        {new Date(chat.createdAt).toLocaleDateString()}
                                      </p>
                                    </>
                                  )}
                                </div>
                                <div className="flex items-center space-x-1 ml-2">
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setEditingChat(chat.id);
                                      setEditingChatName(chat.title);
                                    }}
                                    className="text-gray-400 hover:text-purple-300 transition-colors p-1"
                                  >
                                    <FontAwesomeIcon icon={faEdit} className="text-xs" />
                                  </button>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      showDeleteConfirmation('deleteChat', chat.id, chat.title, () => deleteChat(chat.id));
                                    }}
                                    className="text-red-400 hover:text-red-300 transition-colors p-1"
                                  >
                                    <FontAwesomeIcon icon={faTrash} className="text-xs" />
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-6 text-gray-400">
                            <p className="text-sm">Select a guru first</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Universal Mobile Navigation - Always visible */}
              <div className="border-t border-gradient-to-r from-purple-500/30 to-blue-500/30 pt-6 mt-6">
                {/* Navigation Header */}
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Navigation</h3>
                </div>

                {/* About Mobile */}
                <button
                  onClick={() => {
                    navigate("/about");
                    setMobileMenuOpen(false);
                  }}
                  className="w-full px-5 py-4 text-white hover:bg-gradient-to-r hover:from-purple-600/20 hover:to-blue-600/20 rounded-xl transition-all duration-300 text-left flex items-center space-x-4 mb-3 group border border-transparent hover:border-purple-500/30 animate-mobile-stagger-1"
                >
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <FontAwesomeIcon icon={faInfoCircle} className="text-white text-sm" />
                  </div>
                  <div>
                    <span className="font-medium">About</span>
                    <p className="text-xs text-gray-400 mt-0.5">Learn more about UniGuru</p>
                  </div>
                </button>

                {/* Authentication Section Header */}
                <div className="mb-4 mt-6">
                  <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Account</h3>
                </div>

                {/* Mobile Authentication Section - Always visible */}
                {isLoggedIn ? (
                  <button
                    onClick={() => {
                      onLogout();
                      setMobileMenuOpen(false);
                    }}
                    className="w-full px-5 py-4 text-red-400 hover:bg-gradient-to-r hover:from-red-600/20 hover:to-red-500/20 rounded-xl transition-all duration-300 text-left flex items-center space-x-4 group border border-transparent hover:border-red-500/30 animate-mobile-stagger-2"
                  >
                    <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <FontAwesomeIcon icon={faSignOutAlt} className="text-white text-sm" />
                    </div>
                    <div>
                      <span className="font-medium">Logout</span>
                      <p className="text-xs text-red-300 mt-0.5">Sign out of your account</p>
                    </div>
                  </button>
                ) : (
                  <div className="space-y-3">
                    <button
                      onClick={() => {
                        navigate("/login");
                        setMobileMenuOpen(false);
                      }}
                      className="w-full px-5 py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white rounded-xl transition-all duration-300 text-left flex items-center space-x-4 group shadow-lg hover:shadow-purple-500/25 animate-mobile-stagger-2"
                    >
                      <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                        <FontAwesomeIcon icon={faSignInAlt} className="text-white text-sm" />
                      </div>
                      <div>
                        <span className="font-semibold">Login</span>
                        <p className="text-xs text-purple-100 mt-0.5">Access your account</p>
                      </div>
                    </button>
                    <button
                      onClick={() => {
                        navigate("/signup");
                        setMobileMenuOpen(false);
                      }}
                      className="w-full px-5 py-4 bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-500 hover:to-orange-500 text-white rounded-xl transition-all duration-300 text-left flex items-center space-x-4 group shadow-lg hover:shadow-yellow-500/25 animate-mobile-stagger-3"
                    >
                      <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                        <FontAwesomeIcon icon={faUserPlus} className="text-white text-sm" />
                      </div>
                      <div>
                        <span className="font-semibold">Sign Up</span>
                        <p className="text-xs text-yellow-100 mt-0.5">Create new account</p>
                      </div>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Confirmation Modal */}
      {showConfirmModal && confirmAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 max-w-sm w-full mx-4 shadow-xl">
            <div className="text-center">
              <div className="mb-4">
                <FontAwesomeIcon
                  icon={faTrash}
                  className="text-red-400 text-3xl mb-3"
                />
                <h3 className="text-lg font-semibold text-white mb-2">
                  {confirmAction.type === 'deleteGuru' ? 'Delete Guru' : 'Delete Chat'}
                </h3>
                <p className="text-gray-300 text-sm">
                  Are you sure you want to delete{' '}
                  <span className="font-medium text-white">"{confirmAction.name}"</span>?
                  {confirmAction.type === 'deleteGuru' && (
                    <span className="block mt-1 text-gray-400 text-xs">
                      This will also delete all associated chats.
                    </span>
                  )}
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleCancelDelete}
                  className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmDelete}
                  className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors font-medium"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;