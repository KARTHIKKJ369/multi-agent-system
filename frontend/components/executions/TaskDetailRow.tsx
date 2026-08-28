"use client";

import { useState } from "react";
import { CaretDown, CaretUp, Cpu, Timer, CurrencyDollar, ArrowBendDownRight } from "@phosphor-icons/react";
import { TaskModel } from "@/lib/types";
import { StatusBadge } from "../shared/StatusBadge";
import { formatCurrency, formatDuration, formatNumber } from "@/lib/utils";
import { CodeBlock } from "../shared/CodeBlock";

interface TaskDetailRowProps {
  task: TaskModel;
  defaultOpen?: boolean;
}

export function TaskDetailRow({ task, defaultOpen = false }: TaskDetailRowProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="overflow-hidden rounded-xl border border-zinc-800 bg-[#0e0e11] card-shine transition-all">
      {/* Header Row */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex cursor-pointer flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 hover:bg-zinc-900/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-900 border border-zinc-800 text-emerald-400">
            <Cpu size={16} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-zinc-100 font-mono">
                {task.name}
              </span>
              <span className="rounded bg-zinc-800/80 px-2 py-0.5 text-[10px] text-zinc-400 font-mono capitalize">
                {task.agent_type}
              </span>
            </div>
            <p className="text-xs text-zinc-500 font-mono mt-0.5 line-clamp-1">
              {task.description}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono self-end sm:self-auto">
          <div className="flex items-center gap-3 text-zinc-400">
            <span className="flex items-center gap-1">
              <Timer size={13} className="text-zinc-500" />
              {task.execution_time ? formatDuration(task.execution_time) : "0.5s"}
            </span>
            <span className="flex items-center gap-1">
              <Cpu size={13} className="text-zinc-500" />
              {formatNumber(task.tokens_used || 650)} tkn
            </span>
          </div>

          <StatusBadge status={task.status} size="sm" />

          <button className="text-zinc-400 hover:text-zinc-200">
            {isOpen ? <CaretUp size={14} /> : <CaretDown size={14} />}
          </button>
        </div>
      </div>

      {/* Expanded Accordion Body */}
      {isOpen && (
        <div className="border-t border-zinc-800/80 bg-zinc-950/60 p-4 space-y-4 text-xs font-mono">
          {/* Dependencies */}
          {task.dependencies && task.dependencies.length > 0 && (
            <div className="flex items-center gap-2 text-zinc-400">
              <ArrowBendDownRight size={14} className="text-zinc-500" />
              <span className="text-zinc-500">Dependencies:</span>
              {task.dependencies.map((dep) => (
                <span
                  key={dep}
                  className="rounded bg-zinc-900 border border-zinc-800 px-2 py-0.5 text-[11px] text-zinc-300"
                >
                  {dep}
                </span>
              ))}
            </div>
          )}

          {/* Task Result Output */}
          {task.result && (
            <div>
              <span className="text-zinc-400 uppercase tracking-wider text-[10px] block mb-1.5">
                Task Output
              </span>
              <CodeBlock
                code={typeof task.result === "string" ? task.result : JSON.stringify(task.result, null, 2)}
                language="text"
                maxHeight="max-h-48"
              />
            </div>
          )}

          {/* Error Details if any */}
          {task.error && (
            <div className="rounded-lg bg-rose-950/40 border border-rose-800/60 p-3 text-rose-300">
              <span className="font-bold block mb-1">Execution Failure:</span>
              <p>{task.error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
