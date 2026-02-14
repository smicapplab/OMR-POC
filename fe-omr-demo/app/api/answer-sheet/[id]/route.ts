import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";

export async function GET(
    req: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;

    const session = await getServerSession(authOptions);

    if (!session?.user?.jwt) {
        return NextResponse.json(
            { message: "Unauthorized" },
            { status: 401 }
        );
    }

    const res = await fetch(
        `${process.env.NEXT_API_URL}/answer-sheet/${id}`,
        {
            method: "GET",
            headers: {
                Authorization: `Bearer ${session.user.jwt}`,
            },
        }
    );

    if (res.status === 404) {
        return NextResponse.json(null, { status: 404 });
    }

    const raw = await res.text();

    if (!raw) {
        return NextResponse.json(null, { status: res.status });
    }

    let data;

    try {
        data = JSON.parse(raw);
    } catch {
        return NextResponse.json(
            { message: "Invalid JSON response from API" },
            { status: 502 }
        );
    }

    return NextResponse.json(data, { status: res.status });
}