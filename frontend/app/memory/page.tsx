"use client";

import { MemoryBento } from "@/components/memory/MemoryBento";
import { HardDrives } from "@phosphor-icons/react";

export default function MemoryPage() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <HardDrives size={20} className="text-emerald-400" weight="duotone" />
          <h2 className="text-lg font-bold tracking-tight text-zinc-100 font-mono">
            Memory Stores & Telemetry
          </h2>
        </div>
        <p className="text-xs text-zinc-400 font-mono">
          State persistence, vector embedding caches, and real-time multi-agent execution telemetry.
        </p>
      </div>

      <MemoryBento />
    </div>
  );
}
