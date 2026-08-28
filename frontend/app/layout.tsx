import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { ToastContainer } from "@/components/shared/Toast";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Multi-Agent System Console",
  description: "Autonomous Agent Orchestration, DAG Task Graphs, and Memory Console",
};

export const viewport: Viewport = {
  themeColor: "#09090b",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} dark antialiased`}
    >
      <body className="min-h-[100dvh] bg-[#09090b] text-zinc-100 flex flex-col selection:bg-emerald-400 selection:text-zinc-950">
        <div className="flex min-h-[100dvh] w-full">
          <Sidebar />
          <div className="flex flex-1 flex-col min-w-0 md:pl-64">
            <TopBar />
            <main className="flex-1 p-4 md:p-8 max-w-[1400px] w-full mx-auto">
              {children}
            </main>
          </div>
        </div>
        <ToastContainer />
      </body>
    </html>
  );
}
