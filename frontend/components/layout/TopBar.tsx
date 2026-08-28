"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { List, CheckCircle, WarningCircle, Sparkle } from "@phosphor-icons/react";
import { useAppStore } from "@/lib/store";
import { api } from "@/lib/api";
import { HealthCheckResponse } from "@/lib/types";

const ROUTE_NAMES: Record<string, string> = {
  "/dashboard": "Playground & Live Orchestrator",
  "/executions": "Execution Task Graphs",
  "/agents": "Agent Registry & Capabilities",
  "/conversations": "Conversation Threads",
  "/memory": "System Memory & Telemetry",
};

export function TopBar() {
  const pathname = usePathname();
  const { toggleSidebar } = useAppStore();
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);

  useEffect(() => {
    let isMounted = true;
    const check = async () => {
      try {
        const res = await api.checkHealth();
        if (isMounted) setHealth(res);
      } catch {
        if (isMounted) {
          setHealth({
            status: "offline",
            app_name: "multi-agent-system",
            version: "1.0.0",
            environment: "development",
          });
        }
      }
    };

    check();
    const interval = setInterval(check, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const pageTitle = ROUTE_NAMES[pathname] || "Multi-Agent System";

  const isHealthy = health?.status === "healthy" || health?.status === "connected_mock";

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-zinc-800 bg-[#09090b]/80 backdrop-blur-md px-4 md:px-8">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-900/80 text-zinc-300 hover:bg-zinc-800 hover:text-zinc-100 md:hidden"
          aria-label="Open sidebar"
        >
          <List size={20} />
        </button>

        <div className="flex flex-col">
          <div className="flex items-center gap-2 text-xs font-mono text-zinc-500">
            <span>CONSOLE</span>
            <span>/</span>
            <span className="text-zinc-400 capitalize">
              {pathname.replace("/", "") || "playground"}
            </span>
          </div>
          <h1 className="text-base font-semibold tracking-tight text-zinc-100">
            {pageTitle}
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Backend Health Status Pill */}
        <div className="flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/90 px-3 py-1 text-xs font-mono">
          <span
            className={`inline-block h-2 w-2 rounded-full ${
              isHealthy ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
            }`}
          />
          <span className="text-zinc-300">
            {isHealthy ? "API Active" : "Connecting..."}
          </span>
          <span className="hidden sm:inline text-zinc-600">|</span>
          <span className="hidden sm:inline text-zinc-400 text-[11px]">
            {health?.environment || "dev"}
          </span>
        </div>
      </div>
    </header>
  );
}
