"use client";

import { Cpu, Wrench, ShieldCheck, Sparkle, Sliders } from "@phosphor-icons/react";
import { AgentConfig } from "@/lib/types";

interface AgentCardProps {
  agent: AgentConfig;
}

export function AgentCard({ agent }: AgentCardProps) {
  return (
    <div className="flex flex-col justify-between rounded-xl border border-zinc-800 bg-[#0e0e11] p-5 card-shine card-shine-hover transition-all duration-200">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between gap-2 pb-3 border-b border-zinc-800/70">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-950/60 border border-emerald-800/60 text-emerald-400">
              <Cpu size={18} weight="duotone" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-zinc-100 font-mono tracking-tight">
                {agent.name}
              </h3>
              <span className="text-[11px] text-zinc-500 font-mono uppercase">
                ID: {agent.agent_id}
              </span>
            </div>
          </div>

          <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-400 bg-emerald-950/50 border border-emerald-800/50 px-2 py-0.5 rounded-md">
            Active
          </span>
        </div>

        {/* Description */}
        <p className="mt-3.5 text-xs text-zinc-400 leading-relaxed">
          {agent.description}
        </p>

        {/* Capabilities */}
        <div className="mt-4 space-y-1.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 font-mono">
            Core Capabilities
          </span>
          <div className="flex flex-wrap gap-1.5">
            {agent.capabilities.map((cap) => (
              <span
                key={cap}
                className="rounded-md bg-zinc-900 border border-zinc-800 px-2 py-0.5 text-[11px] text-zinc-300 font-mono"
              >
                {cap}
              </span>
            ))}
          </div>
        </div>

        {/* Tools Attached */}
        <div className="mt-3.5 space-y-1.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500 font-mono flex items-center gap-1">
            <Wrench size={11} />
            Integrated Tools ({agent.tools.length})
          </span>
          <div className="flex flex-wrap gap-1.5">
            {agent.tools.map((tool) => (
              <span
                key={tool}
                className="rounded-md bg-zinc-950 border border-zinc-800/80 px-2 py-0.5 text-[10px] text-emerald-400/90 font-mono"
              >
                {tool}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Model Spec Footer */}
      <div className="mt-5 border-t border-zinc-800/70 pt-3 flex items-center justify-between text-[11px] font-mono text-zinc-500">
        <span>Model: {agent.model || "Nemotron 3"}</span>
        <span>Temp: {agent.temperature ?? 0.2}</span>
      </div>
    </div>
  );
}
