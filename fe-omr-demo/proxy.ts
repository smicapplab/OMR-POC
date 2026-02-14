import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";

export async function proxy(req: NextRequest) {
    const token = await getToken({
        req,
        secret: process.env.NEXTAUTH_SECRET,
    });

    const { pathname } = req.nextUrl;

    // Protect all routes except explicitly public ones
    const isPublic =
        pathname === "/" ||
        pathname.startsWith("/api/auth");

    if (!isPublic && !token) {
        return NextResponse.redirect(new URL("/", req.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: [
        /*
         * Match all request paths except:
         * 1. /api/auth (NextAuth)
         * 2. _next (static files)
         * 3. static files (images, favicon, etc.)
         */
        "/((?!api/auth|_next/static|_next/image|favicon.ico|icon.png).*)",
    ],
};