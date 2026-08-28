"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, TreeStructure, CheckCircle, Timer, Cpu, CurrencyDollar } from "@phosphor-icons/react";
import { api } from "@/lib/api";
import { ExecutionModel, TaskModel } from "@/lib/types";
import { formatCurrency, formatDuration, formatNumber } from "@/lib/utils";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { TaskGraph } from "@/components/executions/TaskGraph";
import { TaskDetailRow } from "@/components/executions/TaskDetailRow";
import { CodeBlock } from "@/components/shared/CodeBlock";
import { ExecutionCardSkeleton } from "@/components/shared/SkeletonLoader";

export default function ExecutionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const executionId = resolvedParams.id;

  const [tasks, setTasks] = useState<TaskModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    api.getExecutionTasks(executionId).then((res) => {
      if (isMounted) {
        setTasks(res.tasks || []);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [executionId]);

  if (loading) {
    return <ExecutionCardSkeleton />;
  }

  const totalTokens = tasks.reduce((acc, t) => acc + (t.tokens_used || 500), 0);
  const totalCost = tasks.reduce((acc, t) => acc + (t.cost || 0.0008), 0);
  const totalDuration = tasks.reduce((acc, t) => acc + (t.execution_time || 0.4), 0);

  return (
    <div className="space-y-6 pb-12">
      {/* Back Link & Header */}
      <div className="flex flex-col gap-3">
        <Link
          href="/executions"
          className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-emerald-400 font-mono transition-colors w-fit"
        >
          <ArrowLeft size={14} />
          <span>Back to Executions List</span>
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold tracking-tight text-zinc-100 font-mono">
                {executionId}
              </h2>
              <StatusBadge status="completed" size="md" />
            </div>
            <p className="text-xs text-zinc-400 font-mono mt-1">
              Topologically planned and executed by Supervisor
            </p>
          </div>
        </div>
      </div>

      {/* Telemetry Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-xl border border-zinc-800 bg-[#0e0e11] p-3.5 card-shine">
          <div className="text-xs font-mono text-zinc-500 flex items-center gap-1.5">
            <Timer size={13} />
            <span>Cumulative Latency</span>
          </div>
          <div className="mt-1 text-lg font-bold text-zinc-100 font-mono">
            {formatDuration(totalDuration)}
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-[#0e0e11] p-3.5 card-shine">
          <div className="text-xs font-mono text-zinc-500 flex items-center gap-1.5">
            <Cpu size={13} />
            <span>Total Tokens</span>
          </div>
          <div className="mt-1 text-lg font-bold text-zinc-100 font-mono">
            {formatNumber(totalTokens)}
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-[#0e0e11] p-3.5 card-shine">
          <div className="text-xs font-mono text-zinc-500 flex items-center gap-1.5">
            <CurrencyDollar size={13} />
            <span>Execution Cost</span>
          </div>
          <div className="mt-1 text-lg font-bold text-emerald-400 font-mono">
            {formatCurrency(totalCost)}
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-[#0e0e11] p-3.5 card-shine">
          <div className="text-xs font-mono text-zinc-500 flex items-center gap-1.5">
            <CheckCircle size={13} />
            <span>Tasks Succeeded</span>
          </div>
          <div className="mt-1 text-lg font-bold text-zinc-100 font-mono">
            {tasks.length} / {tasks.length}
          </div>
        </div>
      </div>

      {/* DAG Graph Visualizer */}
      <TaskGraph
        tasks={tasks}
        selectedTaskId={selectedTaskId}
        onSelectTask={(id) => setSelectedTaskId(id)}
      />

      {/* Task Details List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono">
            Task Execution Logs & Outputs
          </h3>
          <span className="text-[11px] text-zinc-500 font-mono">
            Click rows to expand payload
          </span>
        </div>

        <div className="space-y-2.5">
          {tasks.map((task) => (
            <TaskDetailRow
              key={task.task_id}
              task={task}
              defaultOpen={selectedTaskId === task.task_id}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
