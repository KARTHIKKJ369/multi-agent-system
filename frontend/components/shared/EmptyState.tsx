"use client";

import { ReactNode } from "react";
import { FolderSimpleDashed } from "@phosphor-icons/react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  title: string;
  description: string;
  action?: ReactNode;
  icon?: ReactNode;
  className?: string;
}

export function EmptyState({
  title,
  description,
  action,
  icon,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 bg-zinc-950/40 p-8 text-center",
        className
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-400 mb-4">
        {icon || <FolderSimpleDashed size={24} weight="duotone" />}
      </div>
      <h3 className="text-sm font-semibold text-zinc-200 tracking-tight">
        {title}
      </h3>
      <p className="mt-1 text-xs text-zinc-500 max-w-sm leading-relaxed">
        {description}
      </p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
