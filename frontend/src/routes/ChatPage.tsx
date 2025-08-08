import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import ChatContainer from "../components/ChatContainer";
import LoadingSpinner from "../components/LoadingSpinner";
import { useGuru } from "../context/GuruContext";
import { useChat } from "../context/ChatContext";
import LeftSidebar from "../components/LeftSidebar";

interface ChatPageProps {
  onCreateNewChat?: () => void;
  isCreatingChat?: boolean;
}

const ChatPage: React.FC<ChatPageProps> = ({ onCreateNewChat, isCreatingChat }) => {
  const { selectedGuru } = useGuru();
  const { createNewChatManually, isLoading: isChatLoading } = useChat();
  const [isCreatingChatLocal, setIsCreatingChatLocal] = useState(false);
  const [isPageLoading, setIsPageLoading] = useState(true);

  // Use props if provided, otherwise use local state
  const actualIsCreatingChat = isCreatingChat !== undefined ? isCreatingChat : isCreatingChatLocal;

  // Simulate page loading for better UX
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsPageLoading(false);
    }, 800); // Short delay to show loading state

    return () => clearTimeout(timer);
  }, []);

  // Show loading screen while page is initializing
  if (isPageLoading || isChatLoading) {
    return (
      <div className="relative h-screen overflow-hidden">
        <div className="flex items-center justify-center h-full">
          <div className="bg-glass-card backdrop-blur-xl rounded-xl p-8 border border-glass-border shadow-glass">
            <LoadingSpinner
              size="large"
              variant="orbit"
              text="Loading chat interface..."
            />
          </div>
        </div>
      </div>
    );
  }

  const handleCreateNewChat = async () => {
    if (!selectedGuru) {
      toast.error("Please select a guru first", {
        icon: '🧙‍♂️'
      });
      return;
    }

    // Use provided handler if available, otherwise use local handler
    if (onCreateNewChat) {
      onCreateNewChat();
      return;
    }

    setIsCreatingChatLocal(true);
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
      setIsCreatingChatLocal(false);
    }
  };

  return (
    <div className="relative h-screen overflow-hidden">
      {/* Main Chat Layout */}
      <div className="flex h-screen relative z-10 pt-16 overflow-hidden">
        {/* Left Sidebar - Hidden on mobile, visible on larger screens */}
        <div className="hidden lg:block">
          <LeftSidebar onCreateNewChat={handleCreateNewChat} isCreatingChat={actualIsCreatingChat} />
        </div>

        {/* Main Chat Area - Centered and wider */}
        <div className="flex-1 flex justify-center items-stretch overflow-hidden">
          <div className="w-full max-w-7xl flex flex-col overflow-hidden mx-auto">
            {/* Chat Container */}
            <div className="flex-1 overflow-hidden">
              <ChatContainer />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
