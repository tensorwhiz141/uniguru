import React, { useState, useRef, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faChevronRight,
  faChevronLeft,
  faPlus,
  faEdit,
  faTrash,
  faChevronDown,
  faChevronUp,
  faComments,
  faMessage,
  faRefresh,
  faEllipsisV,
  faCheck,
  faTimes,
  faTools,
  faUserGraduate,
  faRobot,
  faCog
} from "@fortawesome/free-solid-svg-icons";
import toast from "react-hot-toast";
import { useAuth } from "../context/AuthContext";
import { useGuru } from "../context/GuruContext";
import { useChat } from "../context/ChatContext";
import { createNewGuru, createCustomGuru } from "../helpers/api-communicator";
import guruLogo from "../assets/guru.png";
import BubblyButton from "./BubblyButton";
import ConfirmationModal from "./ConfirmationModal";

interface LeftSidebarProps {
  onCreateNewChat: () => void;
  isCreatingChat: boolean;
}

interface GuruFormData {
  name: string;
  subject: string;
  description: string;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({ onCreateNewChat, isCreatingChat }) => {
  const { user } = useAuth();
  const { gurus, addGuru, removeGuru, setSelectedGuru, selectedGuru, refreshGurus, selectGuru } = useGuru();
  const { createNewChatManually, chatSessions, getChatsByGuru, selectChat, currentChatId, loadAllChats, deleteChat, renameChat } = useChat();

  const [isCollapsed, setIsCollapsed] = useState(() => {
    // Always default to collapsed (closed) on refresh
    try {
      // Always return true to keep sidebar closed on refresh
      return true;
    } catch {
      return true;
    }
  });
  const [activeSection, setActiveSection] = useState<'gurus' | 'chats' | 'tools'>('gurus');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [isGuruListExpanded, setIsGuruListExpanded] = useState(true);
  const [isChatListExpanded, setIsChatListExpanded] = useState(true);
  const [isToolsExpanded, setIsToolsExpanded] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [formData, setFormData] = useState<GuruFormData>({
    name: "",
    subject: "",
    description: ""
  });

  const [editingChat, setEditingChat] = useState<string | null>(null);
  const [editingChatName, setEditingChatName] = useState("");

  // Confirmation modal states
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    type: 'guru' | 'chat';
    id: string;
    name: string;
  }>({
    isOpen: false,
    type: 'guru',
    id: '',
    name: ''
  });

  const sidebarRef = useRef<HTMLDivElement>(null);

  // Handle click outside to close sidebar on mobile and window resize
  useEffect(() => {
    // Keep sidebar closed by default - no automatic opening based on screen size

    const handleClickOutside = (event: MouseEvent) => {
      if (sidebarRef.current && !sidebarRef.current.contains(event.target as Node)) {
        // Only auto-close on mobile
        if (typeof window !== 'undefined' && window.innerWidth < 1024) {
          setIsCollapsed(true);
        }
      }
    };

    const handleResize = () => {
      if (typeof window !== 'undefined') {
        const isMobile = window.innerWidth < 1024;
        if (isMobile) {
          setIsCollapsed(true);
          // Note: Not saving to localStorage since we want sidebar closed on refresh
        }
        // Keep sidebar closed on all screen sizes - user must manually open
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    window.addEventListener("resize", handleResize);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const handleCreateGuru = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.subject.trim() || !formData.description.trim()) {
      toast.error("Please fill in all fields");
      return;
    }

    toast.loading("Creating guru...", { id: "create-guru" });

    try {
      const newGuru = await createCustomGuru(
        user.id,
        formData.name.trim(),
        formData.subject.trim(),
        formData.description.trim()
      );
      
      addGuru(newGuru);
      setFormData({ name: "", subject: "", description: "" });
      setShowCreateForm(false);
      
      toast.success("Guru created successfully! 🧙‍♂️", {
        id: "create-guru",
        icon: '✨'
      });
    } catch (error) {
      console.error("Error creating guru:", error);
      toast.error("Failed to create guru. Please try again.", { id: "create-guru" });
    }
  };

  const handleDeleteGuru = (guruId: string, guruName: string) => {
    setConfirmModal({
      isOpen: true,
      type: 'guru',
      id: guruId,
      name: guruName
    });
  };

  const handleDeleteChat = (chatId: string, chatName: string) => {
    setConfirmModal({
      isOpen: true,
      type: 'chat',
      id: chatId,
      name: chatName
    });
  };

  const confirmDelete = async () => {
    const { type, id } = confirmModal;

    if (type === 'guru') {
      toast.loading("Deleting guru...", { id: "delete-guru" });

      try {
        await removeGuru(id);
        toast.success("Guru deleted successfully", {
          id: "delete-guru",
          icon: '🗑️'
        });
      } catch (error) {
        console.error("Error deleting guru:", error);
        toast.error("Failed to delete guru", { id: "delete-guru" });
      }
    } else if (type === 'chat') {
      toast.loading("Deleting chat...", { id: "delete-chat" });

      try {
        await deleteChat(id);
        toast.success("Chat deleted successfully", {
          id: "delete-chat",
          icon: '🗑️'
        });
      } catch (error) {
        console.error("Error deleting chat:", error);
        toast.error("Failed to delete chat", { id: "delete-chat" });
      }
    }
  };

  const handleRenameChat = async (chatId: string, newName: string) => {
    if (!newName.trim()) {
      toast.error("Chat name cannot be empty");
      return;
    }

    toast.loading("Renaming chat...", { id: "rename-chat" });
    
    try {
      await renameChat(chatId, newName.trim());
      setEditingChat(null);
      setEditingChatName("");
      
      toast.success("Chat renamed successfully", {
        id: "rename-chat",
        icon: '✏️'
      });
    } catch (error) {
      console.error("Error renaming chat:", error);
      toast.error("Failed to rename chat", { id: "rename-chat" });
    }
  };

  const toggleGuruList = () => {
    setIsGuruListExpanded(!isGuruListExpanded);
  };

  const toggleChatList = () => {
    setIsChatListExpanded(!isChatListExpanded);
  };

  const toggleToolsList = () => {
    setIsToolsExpanded(!isToolsExpanded);
  };

  const handleRefreshData = async () => {
    setIsRefreshing(true);
    toast.loading("Refreshing data...", { id: "refresh-data" });

    try {
      await Promise.all([
        refreshGurus(),
        loadAllChats()
      ]);
      toast.success("Data refreshed successfully!", {
        id: "refresh-data",
        icon: '✅'
      });
    } catch (error) {
      console.error("Error refreshing data:", error);
      toast.error("Failed to refresh data. Please try again.", { id: "refresh-data" });
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleChatSelect = (chatId: string) => {
    selectChat(chatId);
  };

  const handleGuruSelect = (guru: any) => {
    selectGuru(guru);
    setActiveSection('chats');
  };

  return (
    <>
      {/* Sidebar */}
      <div
        ref={sidebarRef}
        className={`fixed top-16 left-0 h-[calc(100vh-4rem)] transform transition-all duration-300 ease-in-out z-40 backdrop-blur-xl border-r border-purple-400/20 shadow-2xl ${
          isCollapsed ? 'w-16' : 'w-96 lg:w-96'
        }`}
        style={{
          background: "linear-gradient(180deg, rgba(139, 92, 246, 0.08) 0%, rgba(124, 58, 237, 0.06) 30%, rgba(109, 40, 217, 0.05) 70%, rgba(91, 33, 182, 0.04) 100%)",
          backdropFilter: "blur(25px) saturate(120%)",
          borderRight: "1px solid rgba(139, 92, 246, 0.15)",
          boxShadow: "0 25px 50px -12px rgba(139, 92, 246, 0.1), 0 0 0 1px rgba(139, 92, 246, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.05)",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-purple-400/20">
          {!isCollapsed && (
            <h2 className="text-lg font-bold flex items-center gap-2">
              <img src={guruLogo} alt="Guru" className="w-6 h-6 drop-shadow-lg" />
              <span className="bg-gradient-to-r from-purple-300 to-purple-500 bg-clip-text text-transparent">UniGuru Tools</span>
            </h2>
          )}
          <button
            onClick={() => {
              const newCollapsed = !isCollapsed;
              setIsCollapsed(newCollapsed);
              // Note: Not saving to localStorage since we want sidebar closed on refresh
            }}
            className="text-purple-300 hover:text-white transition-all duration-200 p-2 rounded-full hover:bg-purple-400/10"
          >
            <FontAwesomeIcon
              icon={isCollapsed ? faChevronRight : faChevronLeft}
              size="sm"
            />
          </button>
        </div>

        {/* Navigation Tabs */}
        {!isCollapsed && (
          <div className="flex border-b border-purple-400/20">
            <button
              onClick={() => setActiveSection('gurus')}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-all duration-200 ${
                activeSection === 'gurus'
                  ? 'text-purple-300 border-b-2 border-purple-400 bg-purple-400/10'
                  : 'text-gray-300 hover:text-purple-300 hover:bg-purple-400/5'
              }`}
            >
              <FontAwesomeIcon icon={faUserGraduate} className="mr-2" />
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
              <FontAwesomeIcon icon={faComments} className="mr-2" />
              Chats
            </button>
            <button
              onClick={() => setActiveSection('tools')}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-all duration-200 ${
                activeSection === 'tools'
                  ? 'text-purple-300 border-b-2 border-purple-400 bg-purple-400/10'
                  : 'text-gray-300 hover:text-purple-300 hover:bg-purple-400/5'
              }`}
            >
              <FontAwesomeIcon icon={faTools} className="mr-2" />
              Tools
            </button>
          </div>
        )}

        {/* Collapsed Icons */}
        {isCollapsed && (
          <div className="flex flex-col items-center py-4 space-y-4">
            <button
              onClick={() => {
                setIsCollapsed(false);
                setActiveSection('gurus');
              }}
              className="p-3 rounded-xl bg-white/10 hover:bg-white/20 text-white/80 hover:text-white transition-all duration-200 group"
              title="Gurus"
            >
              <FontAwesomeIcon icon={faUserGraduate} className="text-lg group-hover:scale-110 transition-transform" />
            </button>
            <button
              onClick={() => {
                setIsCollapsed(false);
                setActiveSection('chats');
              }}
              className="p-3 rounded-xl bg-white/10 hover:bg-white/20 text-white/80 hover:text-white transition-all duration-200 group"
              title="Chats"
            >
              <FontAwesomeIcon icon={faComments} className="text-lg group-hover:scale-110 transition-transform" />
            </button>
            <button
              onClick={() => {
                setIsCollapsed(false);
                setActiveSection('tools');
              }}
              className="p-3 rounded-xl bg-white/10 hover:bg-white/20 text-white/80 hover:text-white transition-all duration-200 group"
              title="Tools"
            >
              <FontAwesomeIcon icon={faTools} className="text-lg group-hover:scale-110 transition-transform" />
            </button>
            <button
              onClick={onCreateNewChat}
              disabled={isCreatingChat || !selectedGuru}
              className="p-3 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 text-white transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-purple-500/25"
              title="New Chat"
            >
              <FontAwesomeIcon
                icon={faPlus}
                className={`text-lg group-hover:scale-110 transition-transform ${isCreatingChat ? 'animate-spin' : ''}`}
              />
            </button>
          </div>
        )}

        {/* Content */}
        {!isCollapsed && (
          <div className="flex-1 overflow-y-auto sidebar-scroll p-4 space-y-4">
            {/* Gurus Section */}
            {activeSection === 'gurus' && (
              <div className="space-y-4">
                {/* Action Buttons */}
                <div className="flex gap-2">
                  <BubblyButton
                    onClick={() => setShowCreateForm(!showCreateForm)}
                    variant="primary"
                    className="flex-1 flex items-center justify-center gap-2 py-2 px-3 font-medium text-sm"
                  >
                    <FontAwesomeIcon icon={faPlus} className="text-sm" />
                    <span>Create Guru</span>
                  </BubblyButton>
                  <button
                    onClick={handleRefreshData}
                    disabled={isRefreshing}
                    className="text-purple-300 hover:text-white transition-all duration-200 p-2 rounded-full hover:bg-purple-400/10 disabled:opacity-50"
                    title="Refresh"
                  >
                    <FontAwesomeIcon
                      icon={faRefresh}
                      size="sm"
                      className={isRefreshing ? 'animate-spin' : ''}
                    />
                  </button>
                </div>

                {/* Create New Guru Form */}
                {showCreateForm && (
                  <div className="bg-gradient-to-br from-purple-900/40 to-purple-800/30 backdrop-blur-sm rounded-xl p-6 border border-purple-400/30 shadow-xl">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <FontAwesomeIcon icon={faPlus} className="text-white text-sm" />
                      </div>
                      <h3 className="text-white font-semibold text-lg">Create New Guru</h3>
                    </div>

                    <form onSubmit={handleCreateGuru} className="space-y-4">
                      <div>
                        <label className="block text-purple-200 text-sm font-medium mb-2">
                          Guru Name *
                        </label>
                        <input
                          type="text"
                          placeholder="Enter guru name..."
                          value={formData.name}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          className="w-full px-4 py-3 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-purple-200 text-sm font-medium mb-2">
                          Subject/Expertise *
                        </label>
                        <input
                          type="text"
                          placeholder="e.g., Math, Physics, Programming..."
                          value={formData.subject}
                          onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                          className="w-full px-4 py-3 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-purple-200 text-sm font-medium mb-2">
                          Description
                        </label>
                        <textarea
                          placeholder="Describe your guru's personality..."
                          value={formData.description}
                          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                          className="w-full px-4 py-3 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 transition-all resize-none"
                          rows={4}
                        />
                      </div>

                      <div className="flex gap-3 pt-2">
                        <button
                          type="button"
                          onClick={() => setShowCreateForm(false)}
                          className="flex-1 py-3 px-4 bg-gray-600/50 hover:bg-gray-600/70 text-gray-200 rounded-lg transition-all duration-200 font-medium"
                        >
                          Cancel
                        </button>
                        <BubblyButton
                          type="submit"
                          variant="primary"
                          className="flex-1 py-3 px-4 font-medium"
                        >
                          Create Guru
                        </BubblyButton>
                      </div>
                    </form>
                  </div>
                )}

                {/* Gurus List */}
                <div>
                  <button
                    onClick={toggleGuruList}
                    className="flex items-center justify-between w-full text-left mb-3 text-purple-300 hover:text-white transition-colors py-2"
                  >
                    <span className="text-base font-semibold">
                      My Gurus ({gurus.length})
                    </span>
                    <FontAwesomeIcon
                      icon={isGuruListExpanded ? faChevronUp : faChevronDown}
                      className="text-sm"
                    />
                  </button>

                  {isGuruListExpanded && (
                    <div className="space-y-2 max-h-60 overflow-y-auto sidebar-scroll">
                      {gurus.length === 0 ? (
                        <div className="text-gray-300 text-center py-4">
                          <p className="text-sm">No gurus yet</p>
                          <p className="text-xs">Create your first guru to get started!</p>
                        </div>
                      ) : (
                        gurus.map((guru) => (
                          <div
                            key={guru.id}
                            className={`backdrop-blur-sm rounded-lg p-3 border transition-all duration-300 relative group hover:scale-[1.02] cursor-pointer ${
                              selectedGuru?.id === guru.id
                                ? "border-purple-400/50 shadow-lg shadow-purple-500/20"
                                : "border-purple-400/30 hover:border-purple-400/50"
                            }`}
                            style={{
                              background: selectedGuru?.id === guru.id
                                ? "linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(124, 58, 237, 0.1))"
                                : "rgba(139, 92, 246, 0.05)",
                            }}
                            onClick={() => handleGuruSelect(guru)}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1 min-w-0">
                                <h4 className="text-white font-medium text-sm truncate">
                                  {guru.name}
                                </h4>
                                <p className="text-purple-300 text-xs mt-1 truncate">
                                  {guru.subject}
                                </p>
                                <p className="text-gray-300 text-xs mt-1 line-clamp-2">
                                  {guru.description}
                                </p>
                              </div>
                              <div className="flex items-center gap-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteGuru(guru.id, guru.name);
                                  }}
                                  className="p-1 rounded transition-colors text-gray-400 hover:text-red-400"
                                  title="Delete guru"
                                >
                                  <FontAwesomeIcon
                                    icon={faTrash}
                                    size="xs"
                                  />
                                </button>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Chats Section */}
            {activeSection === 'chats' && (
              <div className="space-y-4">
                {/* New Chat Button */}
                <BubblyButton
                  onClick={onCreateNewChat}
                  disabled={isCreatingChat || !selectedGuru}
                  variant="primary"
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 font-medium text-sm"
                >
                  <FontAwesomeIcon
                    icon={isCreatingChat ? faComments : faPlus}
                    className={`text-sm ${isCreatingChat ? 'animate-pulse' : ''}`}
                  />
                  <span>{isCreatingChat ? "Creating..." : "New Chat"}</span>
                </BubblyButton>

                {selectedGuru ? (
                  <div>
                    <button
                      onClick={toggleChatList}
                      className="flex items-center justify-between w-full text-left mb-3 text-purple-300 hover:text-white transition-colors py-2"
                    >
                      <span className="text-base font-semibold">
                        Chat Sessions ({getChatsByGuru(selectedGuru.id).length})
                      </span>
                      <FontAwesomeIcon
                        icon={isChatListExpanded ? faChevronUp : faChevronDown}
                        className="text-sm"
                      />
                    </button>

                    {isChatListExpanded && (
                      <div className="space-y-2 max-h-60 overflow-y-auto scrollbar-hide">
                        {getChatsByGuru(selectedGuru.id).length === 0 ? (
                          <div className="text-gray-300 text-center py-4">
                            <p className="text-sm">No chat sessions yet</p>
                            <p className="text-xs">Create your first chat to get started!</p>
                          </div>
                        ) : (
                          getChatsByGuru(selectedGuru.id).map((chat) => (
                            <div
                              key={chat.id}
                              className={`backdrop-blur-sm rounded-lg p-3 border transition-all duration-300 relative group hover:scale-[1.02] cursor-pointer ${
                                currentChatId === chat.id
                                  ? "border-purple-400/50 shadow-lg shadow-purple-500/20"
                                  : "border-purple-400/30 hover:border-purple-400/50"
                              }`}
                              style={{
                                background: currentChatId === chat.id
                                  ? "linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(124, 58, 237, 0.1))"
                                  : "rgba(139, 92, 246, 0.05)",
                              }}
                              onClick={() => handleChatSelect(chat.id)}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                  {editingChat === chat.id ? (
                                    <input
                                      type="text"
                                      value={editingChatName}
                                      onChange={(e) => setEditingChatName(e.target.value)}
                                      onBlur={() => {
                                        if (editingChatName.trim()) {
                                          handleRenameChat(chat.id, editingChatName);
                                        } else {
                                          setEditingChat(null);
                                          setEditingChatName("");
                                        }
                                      }}
                                      onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                          if (editingChatName.trim()) {
                                            handleRenameChat(chat.id, editingChatName);
                                          } else {
                                            setEditingChat(null);
                                            setEditingChatName("");
                                          }
                                        } else if (e.key === 'Escape') {
                                          setEditingChat(null);
                                          setEditingChatName("");
                                        }
                                      }}
                                      className="w-full bg-transparent text-white text-sm font-medium border-none outline-none"
                                      autoFocus
                                      onClick={(e) => e.stopPropagation()}
                                    />
                                  ) : (
                                    <h4 className="text-white font-medium text-sm truncate">
                                      {chat.title || `Chat ${chat.id.slice(0, 8)}`}
                                    </h4>
                                  )}
                                  <p className="text-gray-300 text-xs mt-1">
                                    {new Date(chat.createdAt).toLocaleDateString()}
                                  </p>
                                </div>
                                <div className="flex items-center gap-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setEditingChat(chat.id);
                                      setEditingChatName(chat.title || `Chat ${chat.id.slice(0, 8)}`);
                                    }}
                                    className="p-1 rounded text-gray-400 hover:text-purple-400 transition-colors"
                                    title="Rename chat"
                                  >
                                    <FontAwesomeIcon icon={faEdit} size="xs" />
                                  </button>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleDeleteChat(chat.id, chat.title || `Chat ${chat.id.slice(0, 8)}`);
                                    }}
                                    className="p-1 rounded transition-colors text-gray-400 hover:text-red-400"
                                    title="Delete chat"
                                  >
                                    <FontAwesomeIcon
                                      icon={faTrash}
                                      size="xs"
                                    />
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-gray-300 text-center py-8">
                    <p className="text-sm">Select a guru first</p>
                    <p className="text-xs">Choose a guru to view and manage chat sessions</p>
                  </div>
                )}
              </div>
            )}

            {/* Tools Section */}
            {activeSection === 'tools' && (
              <div className="space-y-4">
                <div>
                  <button
                    onClick={toggleToolsList}
                    className="flex items-center justify-between w-full text-left mb-3 text-purple-300 hover:text-white transition-colors py-2"
                  >
                    <span className="text-base font-semibold">Available Tools</span>
                    <FontAwesomeIcon
                      icon={isToolsExpanded ? faChevronUp : faChevronDown}
                      className="text-sm"
                    />
                  </button>

                  {isToolsExpanded && (
                    <div className="space-y-2">
                      {/* AI Assistant Tool */}
                      <div
                        key="ai-assistant"
                        className="backdrop-blur-sm rounded-lg p-3 border border-purple-400/30 hover:border-purple-400/50 transition-all duration-300 cursor-pointer hover:scale-[1.02]"
                        style={{
                          background: "rgba(139, 92, 246, 0.05)",
                        }}
                        onClick={() => toast.info("AI Assistant coming soon!")}
                      >
                        <div className="flex items-center gap-3">
                          <div className="text-purple-400 text-lg">🤖</div>
                          <div>
                            <h4 className="text-white font-medium text-sm">AI Assistant</h4>
                            <p className="text-gray-300 text-xs">Get help with your queries</p>
                          </div>
                        </div>
                      </div>

                      {/* Code Generator Tool */}
                      <div
                        key="code-generator"
                        className="backdrop-blur-sm rounded-lg p-3 border border-purple-400/30 hover:border-purple-400/50 transition-all duration-300 cursor-pointer hover:scale-[1.02]"
                        style={{
                          background: "rgba(139, 92, 246, 0.05)",
                        }}
                        onClick={() => toast.info("Code Generator coming soon!")}
                      >
                        <div className="flex items-center gap-3">
                          <div className="text-purple-400 text-lg">💻</div>
                          <div>
                            <h4 className="text-white font-medium text-sm">Code Generator</h4>
                            <p className="text-gray-300 text-xs">Generate code snippets</p>
                          </div>
                        </div>
                      </div>

                      {/* Study Planner Tool */}
                      <div
                        key="study-planner"
                        className="backdrop-blur-sm rounded-lg p-3 border border-purple-400/30 hover:border-purple-400/50 transition-all duration-300 cursor-pointer hover:scale-[1.02]"
                        style={{
                          background: "rgba(139, 92, 246, 0.05)",
                        }}
                        onClick={() => toast.info("Study Planner coming soon!")}
                      >
                        <div className="flex items-center gap-3">
                          <div className="text-purple-400 text-lg">📚</div>
                          <div>
                            <h4 className="text-white font-medium text-sm">Study Planner</h4>
                            <p className="text-gray-300 text-xs">Plan your learning journey</p>
                          </div>
                        </div>
                      </div>

                      {/* Note Taking Tool */}
                      <div
                        key="note-taking"
                        className="backdrop-blur-sm rounded-lg p-3 border border-purple-400/30 hover:border-purple-400/50 transition-all duration-300 cursor-pointer hover:scale-[1.02]"
                        style={{
                          background: "rgba(139, 92, 246, 0.05)",
                        }}
                        onClick={() => toast.info("Note Taking coming soon!")}
                      >
                        <div className="flex items-center gap-3">
                          <div className="text-purple-400 text-lg">📝</div>
                          <div>
                            <h4 className="text-white font-medium text-sm">Note Taking</h4>
                            <p className="text-gray-300 text-xs">Save and organize your insights</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ ...confirmModal, isOpen: false })}
        onConfirm={confirmDelete}
        title={`Delete ${confirmModal.type === 'guru' ? 'Guru' : 'Chat'}`}
        message={`Are you sure you want to delete "${confirmModal.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />
    </>
  );
};

export default LeftSidebar;
