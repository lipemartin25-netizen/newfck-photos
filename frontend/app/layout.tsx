import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AlbumAI Studio | Intelligent Photo Archiving",
  description: "Automate your photo archiving with AI-powered cropping, color restoration, and facial recognition.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-background antialiased`}>
        {/* Here we would wrap with ThemeProvider, AuthProvider, etc. */}
        {children}
      </body>
    </html>
  );
}
