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
         * - /api/auth (NextAuth)
         * - _next static/image files
         * - favicon/icon
         * - all static files with extensions (images, css, js, etc.)
         */
        "/((?!api/auth|_next/static|_next/image|favicon.ico|icon.png|.*\\.(?:png|jpg|jpeg|gif|svg|webp|ico|css|js|map)$).*)",
    ],
};