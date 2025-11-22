import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { cn } from "@/lib/utils";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Boutique AI Sales Agent",
  description: "AI-powered sales dashboard for fashion boutiques",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={cn(inter.className, "bg-gray-50 text-gray-900")}>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 ml-64">
            <Header />
            <main className="pt-16 p-8">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
