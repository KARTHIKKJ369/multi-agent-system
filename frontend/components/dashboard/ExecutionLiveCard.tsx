"use client";

import Link from "next/link";
import { TreeStructure, Timer, CurrencyDollar, Cpu, CheckCircle, ArrowRight } from "@phosphor-icons/react";
import { useAppStore } from "@/lib/store";
import { formatCurrency, formatDuration, formatNumber } from "@/lib/utils";
import { StatusBadge } from "../shared/StatusBadge";
import { TaskRowSkeleton } from "../shared/SkeletonLoader";

export function ExecutionLiveCard() {
  const { activeExecution, activeExecutionTasks, isRunning } = useAppStore();

  if (!activeExecution && !isRunning) return null;

  if (isRunning) {
    return (
      <div className="rounded-xl border border-zinc-800 bg-[#0e0e11] p-5 space-y-4 card-shine">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-sky-400 animate-ping" />
            <span className="text-xs font-semibold uppercase tracking-wider text-sky-400 font-mono">
              Active Orchestration Pipeline
            </span>
          </div>
          <span className="text-xs font-mono text-zinc-500">
            Dispatching tasks across agents...
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-zinc-900 rounded-full h-1.5 overflow-hidden border border-zinc-800">
          <div className="bg-sky-400 h-1.5 rounded-full w-2/3 transition-all duration-500 animate-pulse" />
        </div>

        <TaskRowSkeleton />
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-zinc-800 bg-[#0e0e11] p-5 card-shine">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-950/60 border border-emerald-800/60 text-emerald-400">
            <CheckCircle size={20} weight="duotone" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-zinc-100 font-mono">
                {activeExecution?.execution_id}
              </span>
              <StatusBadge status="completed" size="sm" />
            </div>
            <p className="text-xs text-zinc-500 font-mono">
              All DAG tasks resolved without errors
            </p>
          </div>
        </div>

        <Link
          href={`/executions/${activeExecution?.execution_id}`}
          className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-800/80 px-3 py-1.5 text-xs font-mono font-medium text-zinc-200 hover:bg-zinc-700 hover:text-white transition-all active:scale-95"
        >
          <span>Inspect DAG Graph</span>
          <ArrowRight size={13} />
        </Link>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-4">
        <div className="rounded-lg bg-zinc-950/70 p-3 border border-zinc-800/70">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-mono">
            <Timer size={14} className="text-zinc-500" />
            <span>Duration</span>
          </div>
          <div className="mt-1 text-lg font-bold text-zinc-100 font-mono">
            {formatDuration(activeExecution?.execution_time || 0)}
          </div>
        </div>

        <div className="rounded-lg bg-zinc-950/70 p-3 border border-zinc-800/70">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-mono">
            <Cpu size={14} className="text-zinc-500" />
            <span>Tokens</span>
          </div>
          <div className="mt-1 text-lg font-bold text-zinc-100 font-mono">
            {formatNumber(activeExecution?.total_tokens || 0)}
          </div>
        </div>

        <div className="rounded-lg bg-zinc-950/70 p-3 border border-zinc-800/70">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-mono">
            <CurrencyDollar size={14} className="text-zinc-500" />
            <span>Total Cost</span>
          </div>
          <div className="mt-1 text-lg font-bold text-emerald-400 font-mono">
            {formatCurrency(activeExecution?.total_cost || 0)}
          </div>
        </div>

        <div className="rounded-lg bg-zinc-950/70 p-3 border border-zinc-800/70">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-mono">
            <CheckCircle size={14} className="text-zinc-500" />
            <span>Confidence</span>
          </div>
          <div className="mt-1 text-lg font-bold text-zinc-100 font-mono">
            {Math.round((activeExecution?.confidence || 0.95) * 100)}%
          </div>
        </div>
      </div>

      {/* Task Summary List */}
      {activeExecutionTasks.length > 0 && (
        <div className="border-t border-zinc-800/80 pt-3">
          <div className="text-xs font-mono uppercase tracking-wider text-zinc-500 pb-2">
            Dispatched Tasks ({activeExecutionTasks.length})
          </div>
          <div className="space-y-2">
            {activeExecutionTasks.map((task) => (
              <div
                key={task.task_id}
                className="flex items-center justify-between rounded-lg bg-zinc-950/40 p-2.5 border border-zinc-800/50 text-xs font-mono"
              >
                <div className="flex items-center gap-2.5 truncate">
                  <span className="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-400 uppercase">
                    {task.agent_type}
                  </span>
                  <span className="text-zinc-200 truncate">{task.name}</span>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-zinc-500 text-[11px]">
                    {task.execution_time ? `${task.execution_time}s` : ""}
                  </span>
                  <StatusBadge status={task.status} size="sm" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
