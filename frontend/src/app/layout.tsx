import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { PlatformLayout } from "@/components/layout/platform-layout";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = {
  variable: "--font-mono",
};

export const metadata: Metadata = {
  title: "Telo AI - Voice Assistant Platform",
  description: "Erstelle und verwalte KI-gestützte Voice Assistants",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de">
      <body
        className={`${inter.variable} ${geistMono.variable} antialiased font-sans`}
      >
        <PlatformLayout>{children}</PlatformLayout>
        <Toaster />
      </body>
    </html>
  );
}
