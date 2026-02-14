import NextAuth from "next-auth/next";
import CredentialsProvider from "next-auth/providers/credentials";

import type { Session, User } from "next-auth";
import type { JWT } from "next-auth/jwt";

export const authOptions = {
    providers: [
        CredentialsProvider({
            name: "Credentials",
            credentials: {
                email: { label: "Email", type: "text" },
                password: { label: "Password", type: "password" },
            },

            async authorize(credentials) {
                if (!credentials?.email || !credentials?.password) {
                    return null;
                }

                const res = await fetch(
                    `${process.env.NEXT_API_URL}/auth/login`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            email: credentials.email,
                            password: credentials.password,
                        }),
                    }
                );

                if (!res.ok) return null;

                const data = await res.json();
                if (!data?.accessToken) return null;

                return {
                    id: String(data.user.id),
                    email: data.user.email,
                    jwt: data.accessToken,
                    firstName: data.user.firstName,
                    lastName: data.user.lastName,
                    role: data.user.role,
                };
            },
        }),
    ],

    session: {
        strategy: "jwt" as const,
    },

    pages: {
        signIn: "/",
    },

    callbacks: {
        async jwt({ token, user }: {
            token: JWT;
            user?: User;
        }) {
            if (user) {
                const u = user as User & {
                    jwt: string;
                    firstName: string;
                    lastName: string;
                    role?: string;
                };

                token.jwt = u.jwt;
                token.firstName = u.firstName;
                token.lastName = u.lastName;
                token.role = u.role;
            }

            return token;
        },

        async session({ session, token }: {
            session: Session;
            token: JWT;
        }) {
            if (session.user) {
                session.user.jwt = token.jwt as string;
                session.user.firstName = token.firstName as string;
                session.user.lastName = token.lastName as string;
                session.user.role = token.role as string | undefined;
            }

            return session;
        },
    },

    secret: process.env.NEXTAUTH_SECRET as string,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };