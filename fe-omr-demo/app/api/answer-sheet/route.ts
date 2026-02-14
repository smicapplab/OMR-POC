import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";

export async function GET(request: Request) {
    const session = await getServerSession(authOptions);

    if (!session?.user?.jwt) {
        return NextResponse.json(
            { message: "Unauthorized" },
            { status: 401 }
        );
    }

    const { searchParams } = new URL(request.url);

    const res = await fetch(
        `${process.env.NEXT_API_URL}/answer-sheet?${searchParams.toString()}`,
        {
            headers: {
                Authorization: `Bearer ${session.user.jwt}`,
            },
        }
    );

    const data = await res.json();

    return NextResponse.json(data, { status: res.status });
}