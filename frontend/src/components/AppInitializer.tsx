import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useGuru } from '../context/GuruContext';
import { useChat } from '../context/ChatContext';
import toast from 'react-hot-toast';

interface AppInitializerProps {
  children: React.ReactNode;
}

const AppInitializer: React.FC<AppInitializerProps> = ({ children }) => {
  const { user, isLoggedIn } = useAuth();
  const { refreshGurus } = useGuru();
  const { initializeChats } = useChat();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const initializeApp = async () => {
      if (isLoggedIn && user && !isInitialized) {
        try {
          console.log('🚀 Initializing UniGuru application...');

          // Show a subtle loading toast
          const loadingToast = toast.loading('Loading...', {
            duration: 0, // Don't auto-dismiss
            icon: '🔄'
          });

          // Initialize gurus first
          await refreshGurus();
          console.log('✅ Gurus loaded');

          // Then initialize chats
          await initializeChats();
          console.log('✅ Chats loaded');

          // Dismiss loading toast and show a brief welcome
          toast.dismiss(loadingToast);
          toast.success(`Welcome back, ${user.name}!`, {
            duration: 2000, // Shorter duration
            icon: '👋'
          });

          setIsInitialized(true);
        } catch (error) {
          console.error('❌ Error initializing app:', error);
          toast.dismiss(); // Dismiss any existing toasts
          toast.error('Failed to load data. Please refresh if needed.', {
            duration: 4000,
            icon: '⚠️'
          });
          setIsInitialized(true); // Set as initialized even on error to prevent infinite loops
        }
      }
    };

    // Add a small delay to prevent multiple rapid initializations
    const timeoutId = setTimeout(initializeApp, 100);
    return () => clearTimeout(timeoutId);
  }, [isLoggedIn, user, isInitialized, refreshGurus, initializeChats]);

  // Reset initialization state when user logs out
  useEffect(() => {
    if (!isLoggedIn) {
      setIsInitialized(false);
    }
  }, [isLoggedIn]);

  return <>{children}</>;
};

export default AppInitializer;
