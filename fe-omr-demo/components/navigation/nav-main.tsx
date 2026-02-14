"use client"

import { ChevronRight } from "lucide-react"

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { SidebarGroup, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarMenuSub, SidebarMenuSubButton, SidebarMenuSubItem } from "@/components/ui/sidebar"
import { usePathname, useRouter } from "next/navigation"
import type { Element } from "@/types/nav.type"


export function NavMain({ items }: { items: Element[] }) {
    const router = useRouter();
    const pathname = usePathname();

    return (
        <SidebarGroup>
            <SidebarMenu>
                {items.map((item) => {

                    const isActive = item.url !== "/" ? pathname.startsWith(item.url) : pathname === "/";
                    const hasChildren = Array.isArray(item.items) && item.items.length > 0

                    return (
                        <SidebarMenuItem key={item.title}>
                            {hasChildren ? (
                                <Collapsible
                                    asChild
                                    defaultOpen={item.isActive}
                                    className="group/collapsible"
                                >
                                    <div>
                                        <CollapsibleTrigger asChild>
                                            <SidebarMenuButton
                                                tooltip={item.title}
                                                className={`transition-colors rounded-md
                                                    ${isActive
                                                        ? "data-[active=true]:bg-primary! data-[active=true]:text-white! font-semibold"
                                                        : "hover:bg-primary/10 hover:text-primary"
                                                    }`}
                                            >
                                                {item.icon && <item.icon />}
                                                <span>{item.title}</span>
                                                <ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                                            </SidebarMenuButton>
                                        </CollapsibleTrigger>
                                        <CollapsibleContent>
                                            <SidebarMenuSub>
                                                {item.items?.map((subItem) => (
                                                    <SidebarMenuSubItem key={subItem.title}>
                                                        <SidebarMenuSubButton asChild>
                                                            <a href={subItem.url}>
                                                                <span>{subItem.title}</span>
                                                            </a>
                                                        </SidebarMenuSubButton>
                                                    </SidebarMenuSubItem>
                                                ))}
                                            </SidebarMenuSub>
                                        </CollapsibleContent>
                                    </div>
                                </Collapsible>
                            ) : (
                                <SidebarMenuButton
                                    isActive={isActive}
                                    tooltip={item.title}
                                    className={`transition-colors
                                         ${isActive
                                            ? "data-[active=true]:bg-primary! data-[active=true]:text-white! font-semibold"
                                            : "hover:bg-primary/10 hover:text-primary"
                                        }`}
                                    onClick={() => {
                                        router.push(item.url);
                                    }}
                                >
                                    {item.icon && <item.icon />}
                                    <span>{item.title}</span>
                                </SidebarMenuButton>
                            )}
                        </SidebarMenuItem>
                    )
                })}
            </SidebarMenu>
        </SidebarGroup>
    )
}
