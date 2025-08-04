import React, { useState } from "react";
import toast from "react-hot-toast";
import ChatContainer from "../components/ChatContainer";
import { useGuru } from "../context/GuruContext";
import { useChat } from "../context/ChatContext";
import LeftSidebar from "../components/LeftSidebar";

const ChatPage: React.FC = () => {
  const { selectedGuru } = useGuru();
  const { createNewChatManually } = useChat();
  const [isCreatingChat, setIsCreatingChat] = useState(false);

  // Removed duplicate welcome toast - handled by AppInitializer

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
      {/* Main Chat Layout */}
      <div className="flex h-screen relative z-10 pt-16 overflow-hidden">
        {/* Left Sidebar - All Tools */}
        <LeftSidebar onCreateNewChat={handleCreateNewChat} isCreatingChat={isCreatingChat} />

        {/* Main Chat Area */}
        <div className="flex-1 flex justify-center overflow-hidden ml-16 lg:ml-80">
          <div className="w-full max-w-4xl flex flex-col overflow-hidden">
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
