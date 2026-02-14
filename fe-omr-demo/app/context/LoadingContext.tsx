"use client";

import React, { createContext, useContext, useState, type ReactNode } from "react";

interface LoadingContextType {
    isLoading: boolean;
    message?: string;
    setIsLoading: (loading: boolean) => void;
    setMessage: (message: string) => void;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

interface LoadingProviderProps {
    children: ReactNode;
}

export const LoadingProvider: React.FC<LoadingProviderProps> = ({ children }) => {
    const [isLoading, _setIsLoading] = useState<boolean>(false);
    const [message, setMessage] = useState<string>("");

    const setIsLoading = (loading: boolean) => {
        if (loading) setMessage("");
        _setIsLoading(loading);
    };

    return (
        <LoadingContext.Provider value={{ isLoading, setIsLoading, message, setMessage }}>
            {children}
        </LoadingContext.Provider>
    );
};

export const useLoading = (): LoadingContextType => {
    const context = useContext(LoadingContext);
    if (!context) {
        throw new Error("useLoading must be used within a LoadingProvider");
    }
    return context;
};