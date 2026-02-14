"use client"

import * as React from "react"

import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarRail, useSidebar } from "@/components/ui/sidebar"
import { NavMain } from "./nav-main"
import { NavUser } from "./nav-user"
import Image from "next/image"
import type { Element } from "@/types/nav.type"
import { Separator } from "../ui/separator"

type DataProps = {
    navMain: Element[];
}

export function AppSidebar({ data, ...props }: React.ComponentProps<typeof Sidebar> & { data: DataProps }) {
    const { state } = useSidebar();

    return (
        <Sidebar collapsible="icon" {...props}>
            <SidebarHeader
                className={`bg-white transition-all duration-300 py-5 ${state === "collapsed" ? "hidden" : "block"
                    }`}
            >
                <div className="flex items-center gap-2 font-bold text-xl text-blue-900">
                    <Image
                        src="/icon.png"
                        alt="Logo"
                        width={30}
                        height={75}
                        priority
                    /> OMR POC
                </div>
            </SidebarHeader>
            <Separator />
            <SidebarContent className="bg-white">
                <NavMain items={data.navMain} />
            </SidebarContent>
            <SidebarFooter className="bg-blue-50">
                <NavUser />
            </SidebarFooter>
            <SidebarRail />
        </Sidebar>
    )
}
