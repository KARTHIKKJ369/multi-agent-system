"use client";

import { ExecutionTable } from "@/components/executions/ExecutionTable";
import { TreeStructure } from "@phosphor-icons/react";

export default function ExecutionsPage() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <TreeStructure size={20} className="text-emerald-400" weight="duotone" />
          <h2 className="text-lg font-bold tracking-tight text-zinc-100 font-mono">
            Execution Task Runs
          </h2>
        </div>
        <p className="text-xs text-zinc-400 font-mono">
          Audit history, token attribution, and multi-agent DAG task execution results.
        </p>
      </div>

      <ExecutionTable />
    </div>
  );
}
