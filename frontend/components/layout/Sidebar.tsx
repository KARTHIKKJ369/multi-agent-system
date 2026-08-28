"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  TerminalWindow,
  TreeStructure,
  Cpu,
  ChatCircleDots,
  HardDrives,
  X,
  Sparkle,
} from "@phosphor-icons/react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/lib/store";

const NAV_ITEMS = [
  {
    label: "Playground",
    href: "/dashboard",
    icon: TerminalWindow,
    description: "Execute and orchestrate agents",
  },
  {
    label: "Executions",
    href: "/executions",
    icon: TreeStructure,
    description: "DAG task graphs & history",
  },
  {
    label: "Agent Registry",
    href: "/agents",
    icon: Cpu,
    description: "Specialized agent profiles",
  },
  {
    label: "Conversations",
    href: "/conversations",
    icon: ChatCircleDots,
    description: "Multi-turn context threads",
  },
  {
    label: "Memory & Metrics",
    href: "/memory",
    icon: HardDrives,
    description: "Redis, Qdrant & telemetry",
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, setSidebarOpen } = useAppStore();

  return (
    <>
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-xs md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={cn(
          "fixed top-0 bottom-0 left-0 z-50 flex w-64 flex-col border-r border-zinc-800 bg-[#0c0c0e] transition-transform duration-200 ease-in-out md:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header Branding */}
        <div className="flex h-16 items-center justify-between border-b border-zinc-800/80 px-5">
          <Link
            href="/dashboard"
            className="flex items-center gap-2.5 group"
            onClick={() => setSidebarOpen(false)}
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 group-hover:border-emerald-500/50 transition-colors">
              <Sparkle size={18} weight="duotone" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold tracking-tight text-zinc-100 font-mono">
                MULTI-AGENT
              </span>
              <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">
                Autonomous System
              </span>
            </div>
          </Link>

          <button
            className="rounded-md p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100 md:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 space-y-1.5 px-3 py-4">
          <div className="px-2 pb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-500 font-mono">
            Navigation
          </div>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname?.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                  isActive
                    ? "bg-zinc-800/90 text-emerald-400 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)] border-l-2 border-emerald-400"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
                )}
              >
                <Icon
                  size={18}
                  weight={isActive ? "fill" : "regular"}
                  className={cn(
                    "transition-colors",
                    isActive
                      ? "text-emerald-400"
                      : "text-zinc-400 group-hover:text-zinc-200"
                  )}
                />
                <div className="flex flex-col">
                  <span>{item.label}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Footer Meta */}
        <div className="border-t border-zinc-800/80 p-4">
          <div className="rounded-lg bg-zinc-900/60 p-3 border border-zinc-800/60">
            <div className="flex items-center justify-between text-xs">
              <span className="text-zinc-400 font-mono">Supervisor v1.0.0</span>
              <span className="inline-flex items-center gap-1.5 text-[11px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/50">
                Ready
              </span>
            </div>
            <div className="mt-2 text-[11px] text-zinc-400 font-mono">
              Groq: GPT-OSS 120B
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
