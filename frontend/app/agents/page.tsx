"use client";

import { AgentGrid } from "@/components/agents/AgentGrid";
import { Cpu } from "@phosphor-icons/react";

export default function AgentsPage() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <Cpu size={20} className="text-emerald-400" weight="duotone" />
          <h2 className="text-lg font-bold tracking-tight text-zinc-100 font-mono">
            Autonomous Agent Registry
          </h2>
        </div>
        <p className="text-xs text-zinc-400 font-mono">
          Specialized autonomous agents, capability matrix, and tool assignments orchestrated by Supervisor.
        </p>
      </div>

      <AgentGrid />
    </div>
  );
}
