import React, { createContext, useContext, useState, ReactNode } from 'react';
import { deleteGuru, deleteUserChats, fetchUserGurus } from '../helpers/api-communicator';

// Define the context type
interface GuruContextType {
    selectedGuru: Guru | null;
    setSelectedGuru: (guru: Guru | null) => void;
    clearUserChats: () => void;
    deleteGurus: (guruId: string) => void;
    gurus: Guru[];
    setGurus: (gurus: Guru[]) => void;
    addGuru: (guru: Guru) => void;
    removeGuru: (guruId: string) => void;
    refreshGurus: () => Promise<void>;
    selectGuru: (guru: Guru) => void;
    isLoading: boolean;
}

// Create the context with a default value
const GuruContext = createContext<GuruContextType | undefined>(undefined);

export const useGuru = () => {
    const context = useContext(GuruContext);
    if (!context) {
        throw new Error("useGuru must be used within a GuruProvider");
    }
    return context;
};

// Define a type for the Guru
type Guru = {
    name: string;
    description: string;
    subject: string;
    id: string;
    userid: string;
};

// Create a provider component
export const GuruProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [selectedGuru, setSelectedGuru] = useState<Guru | null>(() => {
        // Restore selected guru from localStorage on initialization
        try {
            const stored = localStorage.getItem('uniguru_selected_guru');
            return stored ? JSON.parse(stored) : null;
        } catch {
            return null;
        }
    });
    const [gurus, setGurus] = useState<Guru[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const clearUserChats = async () => {
        // Call API to clear user chats
        try {
            await deleteUserChats();
            setSelectedGuru(null);
        } catch (error) {
            console.error("Failed to clear chats:", error);
        }
    };

    const deleteGurus = async (guruId: string) => {
        // Call API to delete guru
        try {
            await deleteGuru(guruId);
            setSelectedGuru(null);
        } catch (error) {
            console.error("Failed to delete guru:", error);
        }
    };

    const addGuru = (guru: Guru) => {
        setGurus(prev => {
            const updated = [...prev, guru];
            if (prev.length === 0) {
                setSelectedGuru(guru);
            }
            return updated;
        });
    };

    const removeGuru = async (guruId: string) => {
        try {
            await deleteGuru(guruId);
            setGurus(prev => {
                const updated = prev.filter(guru => guru.id !== guruId);
                if (selectedGuru?.id === guruId) {
                    setSelectedGuru(updated[0] || null);
                }
                return updated;
            });
        } catch (error) {
            console.error("Failed to remove guru:", error);
            throw error;
        }
    };

    const refreshGurus = async () => {
        try {
            setIsLoading(true);
            const userGurus = await fetchUserGurus();
            setGurus(userGurus || []);

            // Auto-select first guru if none selected
            if (!selectedGuru && userGurus && userGurus.length > 0) {
                setSelectedGuru(userGurus[0]);
            }
        } catch (error) {
            console.error("Failed to refresh gurus:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const selectGuru = (guru: Guru) => {
        setSelectedGuru(guru);
        // Save to localStorage for persistence across refreshes
        try {
            localStorage.setItem('uniguru_selected_guru', JSON.stringify(guru));
        } catch (error) {
            console.warn('Failed to save selected guru to localStorage:', error);
        }
    };

    return (
        <GuruContext.Provider value={{
            selectedGuru,
            setSelectedGuru,
            clearUserChats,
            deleteGurus,
            gurus,
            setGurus,
            addGuru,
            removeGuru,
            refreshGurus,
            selectGuru,
            isLoading
        }}>
            {children}
        </GuruContext.Provider>
    );
};