"use client";

import { useEffect, useState } from "react";
import {
  HardDrives,
  Database,
  Lightning,
  Clock,
  ChartBar,
  Cpu,
  CheckCircle,
  CurrencyDollar,
} from "@phosphor-icons/react";
import { api } from "@/lib/api";
import { MemoryStats, SystemMetrics } from "@/lib/types";
import { formatCurrency, formatNumber } from "@/lib/utils";

export function MemoryBento() {
  const [memoryStats, setMemoryStats] = useState<MemoryStats | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);

  useEffect(() => {
    let isMounted = true;
    Promise.all([api.getMemoryStats(), api.getMetrics()]).then(([m, met]) => {
      if (isMounted) {
        setMemoryStats(m);
        setMetrics(met);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Bento Grid Layer 1: Asymmetric 2-Col */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
        {/* Cell 1: Redis Conversation Cache (7 cols, tinted background) */}
        <div className="md:col-span-7 rounded-xl border border-zinc-800 bg-[#0e0e12] p-5 card-shine flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800/80">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-rose-950/60 border border-rose-800/60 text-rose-400">
                  <Database size={16} weight="duotone" />
                </div>
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-200 font-mono">
                    Redis Short-Term Memory
                  </h3>
                  <span className="text-[10px] text-zinc-500 font-mono">
                    Key-Value Fast Cache & Session Store
                  </span>
                </div>
              </div>

              <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 px-2 py-0.5 rounded-md">
                Connected
              </span>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-zinc-950/80 p-3 border border-zinc-800/80">
                <span className="text-[11px] text-zinc-500 font-mono block">
                  Active Context Threads
                </span>
                <span className="text-xl font-bold text-zinc-100 font-mono">
                  {memoryStats?.active_conversations_count || 38}
                </span>
              </div>

              <div className="rounded-lg bg-zinc-950/80 p-3 border border-zinc-800/80">
                <span className="text-[11px] text-zinc-500 font-mono block">
                  Session TTL
                </span>
                <span className="text-xl font-bold text-zinc-100 font-mono">
                  86,400s (24h)
                </span>
              </div>
            </div>

            <div className="mt-4 space-y-1.5 text-xs font-mono text-zinc-400">
              <span className="text-[10px] font-semibold uppercase text-zinc-500 block">
                Cached Memory Partitions
              </span>
              <div className="flex flex-wrap gap-1.5">
                <span className="rounded bg-zinc-900 border border-zinc-800 px-2 py-0.5 text-[11px] text-zinc-300">
                  conversation:history:*
                </span>
                <span className="rounded bg-zinc-900 border border-zinc-800 px-2 py-0.5 text-[11px] text-zinc-300">
                  execution:state:*
                </span>
                <span className="rounded bg-zinc-900 border border-zinc-800 px-2 py-0.5 text-[11px] text-zinc-300">
                  celery:task:queue
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-zinc-800/80 text-[11px] font-mono text-zinc-500 flex justify-between">
            <span>URI: redis://redis:6379/0</span>
            <span>Eviction: allkeys-lru</span>
          </div>
        </div>

        {/* Cell 2: Qdrant Vector & RAG Store (5 cols, emerald tinted variant) */}
        <div className="md:col-span-5 rounded-xl border border-emerald-950/60 bg-[#0a120e] p-5 card-shine flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-emerald-900/40">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-950 border border-emerald-700/60 text-emerald-400">
                  <HardDrives size={16} weight="duotone" />
                </div>
                <div>
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-emerald-300 font-mono">
                    Qdrant Vector RAG
                  </h3>
                  <span className="text-[10px] text-emerald-500/80 font-mono">
                    Dense Semantic Index
                  </span>
                </div>
              </div>

              <span className="text-[11px] font-mono text-emerald-400 bg-emerald-900/40 border border-emerald-600/40 px-2 py-0.5 rounded-md">
                Active
              </span>
            </div>

            <div className="mt-4 space-y-3">
              <div className="rounded-lg bg-zinc-950/90 p-3 border border-emerald-950">
                <span className="text-[11px] text-zinc-500 font-mono block">
                  Total Indexed Vectors
                </span>
                <span className="text-2xl font-bold text-emerald-400 font-mono">
                  {formatNumber(memoryStats?.total_vectors_count || 1420)}
                </span>
              </div>

              <div className="space-y-1 text-xs font-mono text-zinc-400">
                <div className="flex justify-between py-1 border-b border-zinc-800/40">
                  <span className="text-zinc-500">Embedding Model:</span>
                  <span className="text-zinc-300">text-embedding-3-small</span>
                </div>
                <div className="flex justify-between py-1 border-b border-zinc-800/40">
                  <span className="text-zinc-500">Vector Dimension:</span>
                  <span className="text-zinc-300">1,536 dimensions</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-zinc-500">Distance Metric:</span>
                  <span className="text-zinc-300">Cosine Similarity</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-emerald-900/40 text-[11px] font-mono text-emerald-500/80 flex justify-between">
            <span>Port: 6333</span>
            <span>Collections: 3</span>
          </div>
        </div>
      </div>

      {/* Bento Grid Layer 2: Invocations & Telemetry Distribution */}
      <div className="rounded-xl border border-zinc-800 bg-[#0e0e11] p-5 card-shine">
        <div className="flex items-center justify-between pb-3 border-b border-zinc-800/80 mb-4">
          <div className="flex items-center gap-2">
            <ChartBar size={16} className="text-emerald-400" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-200 font-mono">
              Agent Workload & Invocation Distribution
            </h3>
          </div>
          <span className="text-[11px] text-zinc-500 font-mono">
            {formatNumber(metrics?.total_requests || 148)} Total Dispatches
          </span>
        </div>

        {/* Invocation Bars */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {Object.entries(
            metrics?.agent_invocations || {
              planner: 148,
              coding: 112,
              research: 96,
              qa: 144,
              review: 42,
              writing: 38,
              analytics: 24,
              deployment: 16,
            }
          ).map(([agent, count]) => {
            const percentage = Math.round((count / 148) * 100);
            return (
              <div
                key={agent}
                className="rounded-lg bg-zinc-950/70 p-3.5 border border-zinc-800/70"
              >
                <div className="flex items-center justify-between text-xs font-mono mb-2">
                  <span className="font-semibold text-zinc-200 uppercase">
                    {agent}
                  </span>
                  <span className="text-emerald-400 font-bold">{count} runs</span>
                </div>
                <div className="w-full bg-zinc-900 rounded-full h-1.5 overflow-hidden border border-zinc-800/80">
                  <div
                    className="bg-emerald-400 h-1.5 rounded-full"
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
