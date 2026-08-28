"use client";

import { useState } from "react";
import { TaskModel } from "@/lib/types";
import { StatusBadge } from "../shared/StatusBadge";
import { formatDuration } from "@/lib/utils";
import { Cpu, ArrowRight, CheckCircle, Clock } from "@phosphor-icons/react";

interface TaskGraphProps {
  tasks: TaskModel[];
  onSelectTask?: (taskId: string) => void;
  selectedTaskId?: string | null;
}

export function TaskGraph({
  tasks,
  onSelectTask,
  selectedTaskId,
}: TaskGraphProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  if (!tasks || tasks.length === 0) {
    return (
      <div className="rounded-xl border border-zinc-800 bg-[#0c0c0e] p-6 text-center text-xs text-zinc-500 font-mono">
        No DAG tasks discovered for this execution.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-zinc-800 bg-[#0c0c0e] p-5 card-shine">
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-5">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-300 font-mono">
            Directed Acyclic Graph (DAG) Pipeline
          </span>
        </div>
        <span className="text-[11px] text-zinc-500 font-mono">
          {tasks.length} Nodes &bull; Topologically Sorted
        </span>
      </div>

      {/* DAG Flow Visualizer */}
      <div className="relative overflow-x-auto py-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 min-w-[700px]">
          {tasks.map((task, idx) => {
            const isSelected = selectedTaskId === task.task_id;
            const isHovered = hoveredId === task.task_id;

            return (
              <div key={task.task_id} className="flex items-center flex-1">
                {/* Node Box */}
                <div
                  onClick={() => onSelectTask && onSelectTask(task.task_id)}
                  onMouseEnter={() => setHoveredId(task.task_id)}
                  onMouseLeave={() => setHoveredId(null)}
                  className={`cursor-pointer rounded-xl border p-4 transition-all duration-200 w-full relative ${
                    isSelected
                      ? "border-emerald-400 bg-zinc-900 shadow-md shadow-emerald-950/40 ring-1 ring-emerald-400"
                      : isHovered
                      ? "border-zinc-700 bg-zinc-900/90"
                      : "border-zinc-800 bg-zinc-950/80"
                  }`}
                >
                  {/* Step Number Pill */}
                  <div className="flex items-center justify-between mb-2">
                    <span className="rounded bg-zinc-800/90 px-1.5 py-0.5 text-[10px] font-mono text-zinc-400 font-bold">
                      STAGE {idx + 1}
                    </span>
                    <StatusBadge status={task.status} size="sm" />
                  </div>

                  {/* Task Name */}
                  <h4 className="text-xs font-semibold text-zinc-100 font-mono tracking-tight line-clamp-1">
                    {task.name}
                  </h4>

                  {/* Agent Tag */}
                  <div className="mt-2.5 flex items-center justify-between border-t border-zinc-800/70 pt-2 text-[11px] font-mono text-zinc-400">
                    <span className="flex items-center gap-1 text-emerald-400 font-medium capitalize">
                      <Cpu size={12} />
                      {task.agent_type}
                    </span>
                    <span className="text-zinc-500">
                      {task.execution_time ? formatDuration(task.execution_time) : "0.4s"}
                    </span>
                  </div>
                </div>

                {/* Connector Arrow */}
                {idx < tasks.length - 1 && (
                  <div className="flex items-center justify-center px-2 text-zinc-600 shrink-0">
                    <ArrowRight size={18} weight="bold" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
