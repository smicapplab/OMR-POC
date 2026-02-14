import type { DefaultSession } from "next-auth";

declare module "next-auth" {
    interface Session {
        user?: DefaultSession["user"] & {
            id: string;
            jwt: string;
            role?: string;
            firstName: string;
            lastName: string;
        };
    }

    interface User {
        jwt: string;
    }
}

declare module "next-auth/jwt" {
    interface JWT {
        jwt?: string;
    }
}