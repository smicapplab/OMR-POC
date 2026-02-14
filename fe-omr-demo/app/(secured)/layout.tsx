import LayoutClient from "./layout-client";

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {

    return (
        <LayoutClient>
            {children}
        </LayoutClient>
    );
}
