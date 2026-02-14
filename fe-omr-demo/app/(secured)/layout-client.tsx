"use client";

import { AppSidebar } from "@/components/navigation/app-sidebar";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { LayoutDashboard } from "lucide-react";
import { usePathname } from "next/navigation";

const data = {
    navMain: [
        {
            title: "Dashboard",
            url: "/dashboard",
            icon: LayoutDashboard,
            isActive: true,
        },
    ],
};

export default function LayoutClient({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();

    const deriveTitle = () => {
        if (!pathname) return "";

        const segments = pathname.split("/").filter(Boolean);
        const lastSegment = segments[segments.length - 1] || "dashboard";

        // If dynamic route like /answer-sheet/3, use previous segment
        const titleSegment = isNaN(Number(lastSegment))
            ? lastSegment
            : segments[segments.length - 2] || "dashboard";

        return titleSegment
            .split("-")
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");
    };

    return (
        <SidebarProvider>
            <AppSidebar data={data} />
            <SidebarInset>
                <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
                    <div className="flex items-center gap-2 px-4">
                        <SidebarTrigger className="-ml-1" />
                        <Separator
                            orientation="vertical"
                            className="mr-2 data-[orientation=vertical]:h-4"
                        />
                        {deriveTitle()}
                    </div>
                </header>
                {children}
            </SidebarInset>
        </SidebarProvider>
    );
}