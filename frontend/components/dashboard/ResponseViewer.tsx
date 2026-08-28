"use client";

import { useAppStore } from "@/lib/store";
import { CodeBlock } from "../shared/CodeBlock";
import { EmptyState } from "../shared/EmptyState";
import { TerminalWindow } from "@phosphor-icons/react";

export function ResponseViewer() {
  const { activeExecution, isRunning } = useAppStore();

  if (isRunning) return null;

  if (!activeExecution || !activeExecution.response) {
    return (
      <EmptyState
        title="Ready for Prompt Execution"
        description="Submit an objective in the supervisor composer above to trigger multi-agent DAG execution."
        icon={<TerminalWindow size={24} className="text-zinc-500" />}
        className="mt-6"
      />
    );
  }

  return (
    <div className="mt-6 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono">
          Final Synthesized Agent Output
        </h3>
        <span className="text-[11px] text-zinc-500 font-mono">
          Execution ID: {activeExecution.execution_id}
        </span>
      </div>

      <CodeBlock
        code={activeExecution.response}
        language="markdown"
        title="Synthesized Output"
        maxHeight="max-h-[500px]"
      />
    </div>
  );
}
