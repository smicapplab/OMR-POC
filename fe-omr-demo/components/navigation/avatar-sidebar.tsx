import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { getBackgroundColor, getFallbackText } from "@/lib/utils";
import { useSession } from "next-auth/react";

export function AvatarSidebar() {
    const { data: session } = useSession();
    if (!session) {
        return null;
    }

    const fallbackColor = getBackgroundColor(session?.user?.name);
    return (
        <>
            <Avatar className="h-8 w-8 rounded-lg">
                <AvatarFallback
                    style={{ backgroundColor: fallbackColor }}
                    className={`rounded-lg  text-white`}
                >
                    {getFallbackText(session?.user?.firstName || "", session?.user?.lastName || "")}
                </AvatarFallback>
            </Avatar>
            <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold!">{session?.user?.firstName} {session?.user?.lastName}</span>
                <span className="truncate text-xs">{session?.user?.email} </span>
            </div>
        </>
    );
}