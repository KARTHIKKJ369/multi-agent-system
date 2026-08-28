"use client";

import { CheckCircle, Clock, PlayCircle, XCircle, Prohibit, Circle } from "@phosphor-icons/react";
import { cn } from "@/lib/utils";
import { ExecutionStatus, TaskStatus } from "@/lib/types";

interface StatusBadgeProps {
  status: ExecutionStatus | TaskStatus | string;
  className?: string;
  size?: "sm" | "md";
}

export function StatusBadge({ status, className, size = "md" }: StatusBadgeProps) {
  const normalized = status.toLowerCase();

  let label = status;
  let bgClasses = "bg-zinc-800 text-zinc-300 border-zinc-700";
  let Icon = Circle;

  switch (normalized) {
    case "completed":
    case "success":
      label = "Completed";
      bgClasses = "bg-emerald-950/60 text-emerald-400 border-emerald-800/60";
      Icon = CheckCircle;
      break;
    case "running":
    case "active":
    case "in_progress":
      label = "Running";
      bgClasses = "bg-sky-950/60 text-sky-400 border-sky-800/60 animate-pulse";
      Icon = PlayCircle;
      break;
    case "pending":
      label = "Pending";
      bgClasses = "bg-amber-950/50 text-amber-400 border-amber-800/50";
      Icon = Clock;
      break;
    case "ready":
      label = "Ready";
      bgClasses = "bg-indigo-950/60 text-indigo-400 border-indigo-800/60";
      Icon = Clock;
      break;
    case "failed":
    case "error":
      label = "Failed";
      bgClasses = "bg-rose-950/60 text-rose-400 border-rose-800/60";
      Icon = XCircle;
      break;
    case "cancelled":
    case "skipped":
      label = "Skipped";
      bgClasses = "bg-zinc-800/80 text-zinc-400 border-zinc-700/80";
      Icon = Prohibit;
      break;
    default:
      label = status;
      break;
  }

  const sizeClasses =
    size === "sm"
      ? "px-2 py-0.5 text-[10px] gap-1"
      : "px-2.5 py-1 text-xs gap-1.5";

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md font-mono font-medium border uppercase tracking-wider",
        bgClasses,
        sizeClasses,
        className
      )}
    >
      <Icon size={size === "sm" ? 12 : 14} weight="bold" />
      {label}
    </span>
  );
}
