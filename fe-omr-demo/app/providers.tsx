"use client";

import { SessionProvider } from "next-auth/react";
import { LoadingProvider } from "./context/LoadingContext";
import { Toaster } from "sonner";
import LoadingOverlay from "@/components/LoadingOverlay";

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <SessionProvider>
            <LoadingProvider>
                {children}
                <Toaster richColors position="bottom-right" />
                <LoadingOverlay />
            </LoadingProvider>
        </SessionProvider>
    );
}