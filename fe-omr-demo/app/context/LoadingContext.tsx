"use client";

import React, { createContext, useContext, useState, useCallback, useMemo, type ReactNode } from "react";

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

    const setIsLoading = useCallback((loading: boolean) => {
        if (loading) setMessage("");
        _setIsLoading(loading);
    }, []);

    const value = useMemo(() => ({
        isLoading,
        setIsLoading,
        message,
        setMessage,
    }), [isLoading, message, setIsLoading]);

    return (
        <LoadingContext.Provider value={value}>
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