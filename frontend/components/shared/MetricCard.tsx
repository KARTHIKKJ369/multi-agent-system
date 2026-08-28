"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon?: ReactNode;
  trend?: string;
  variant?: "default" | "emerald" | "sky" | "amber";
  className?: string;
}

export function MetricCard({
  label,
  value,
  subtext,
  icon,
  trend,
  variant = "default",
  className,
}: MetricCardProps) {
  let accentBorder = "border-zinc-800/80 hover:border-zinc-700/80";
  let iconBg = "bg-zinc-800/80 text-zinc-300 border-zinc-700/60";

  if (variant === "emerald") {
    accentBorder = "border-emerald-900/40 hover:border-emerald-700/50 bg-emerald-950/10";
    iconBg = "bg-emerald-950/60 text-emerald-400 border-emerald-800/50";
  } else if (variant === "sky") {
    accentBorder = "border-sky-900/40 hover:border-sky-700/50 bg-sky-950/10";
    iconBg = "bg-sky-950/60 text-sky-400 border-sky-800/50";
  } else if (variant === "amber") {
    accentBorder = "border-amber-900/40 hover:border-amber-700/50 bg-amber-950/10";
    iconBg = "bg-amber-950/60 text-amber-400 border-amber-800/50";
  }

  return (
    <div
      className={cn(
        "relative flex flex-col justify-between rounded-xl border bg-zinc-900/40 p-4 transition-all duration-200 card-shine",
        accentBorder,
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-zinc-400 font-mono">
          {label}
        </span>
        {icon && (
          <div className={cn("flex h-7 w-7 items-center justify-center rounded-lg border text-sm", iconBg)}>
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold tracking-tight text-zinc-100 font-mono">
          {value}
        </div>
        {(subtext || trend) && (
          <div className="mt-1 flex items-center gap-2 text-xs text-zinc-500 font-mono">
            {trend && (
              <span className="font-semibold text-emerald-400">{trend}</span>
            )}
            {subtext && <span>{subtext}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
