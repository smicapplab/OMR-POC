import type { LucideIcon } from "lucide-react";

export type Element = {
    title: string;
    url: string;
    icon?: LucideIcon,
    isActive?: boolean;
    items?: Item[];
}

export type Item = {
    title: string;
    url?: string;
}