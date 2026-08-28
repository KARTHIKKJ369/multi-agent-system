"use client";

import { useState } from "react";
import { Play, Sparkle, CircleNotch, SlidersHorizontal, CaretDown, CaretUp } from "@phosphor-icons/react";
import { useAppStore } from "@/lib/store";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

const PROMPT_PRESETS = [
  "Research and optimize multi-agent task execution graph for maximum parallel concurrency.",
  "Implement vector index embedding pipeline for technical architecture markdown docs.",
  "Run automated security audit on FastAPI endpoints and verify rate-limiting configs.",
  "Analyze token consumption across specialized coding, planner, and QA agents.",
];

export function RequestComposer() {
  const [message, setMessage] = useState("");
  const [enableReflection, setEnableReflection] = useState(true);
  const [enableQA, setEnableQA] = useState(true);
  const [conversationId, setConversationId] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);

  const {
    isRunning,
    setIsRunning,
    setActiveExecution,
    setActiveExecutionTasks,
    addExecutionHistory,
    addNotification,
  } = useAppStore();

  const handleRun = async () => {
    if (!message.trim() || isRunning) return;

    setIsRunning(true);
    const startTime = Date.now();

    try {
      const result = await api.executeRequest({
        message: message.trim(),
        conversation_id: conversationId.trim() || undefined,
        enable_reflection: enableReflection,
        enable_qa: enableQA,
      });

      setActiveExecution(result);

      // Fetch tasks for this execution
      const tasksRes = await api.getExecutionTasks(result.execution_id);
      setActiveExecutionTasks(tasksRes.tasks);

      // Add to store history
      addExecutionHistory({
        execution_id: result.execution_id,
        user_request: message.trim(),
        status: "completed",
        progress: 1.0,
        completed_tasks: tasksRes.tasks.map((t) => t.task_id),
        failed_tasks: [],
        total_cost: result.total_cost,
        total_tokens: result.total_tokens,
        execution_time: result.execution_time,
        confidence: result.confidence,
        created_at: new Date().toISOString().replace("T", " ").substring(0, 19),
        conversation_id: conversationId.trim() || null,
        response: result.response,
      });

      addNotification("success", `Execution ${result.execution_id} completed successfully`);
    } catch (e: any) {
      addNotification("error", e.message || "Execution request failed");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="rounded-xl border border-zinc-800 bg-[#0e0e11] p-5 card-shine">
      {/* Title & Presets */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3">
        <div className="flex items-center gap-2">
          <Sparkle size={16} className="text-emerald-400" weight="duotone" />
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-300 font-mono">
            Supervisor Prompt Input
          </span>
        </div>
        <span className="text-[11px] text-zinc-400 font-mono">
          Model: Groq / GPT-OSS 120B
        </span>
      </div>

      {/* Main Textarea */}
      <div className="relative mt-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Describe your multi-agent objective or workflow request here..."
          rows={4}
          disabled={isRunning}
          className="w-full rounded-lg border border-zinc-800 bg-zinc-950/80 p-3.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-emerald-500/80 focus:outline-hidden focus:ring-1 focus:ring-emerald-500/40 font-mono transition-all resize-y disabled:opacity-60"
        />
      </div>

      {/* Presets Chips */}
      <div className="mt-3 flex flex-wrap items-center gap-1.5">
        <span className="text-[11px] text-zinc-500 font-mono mr-1">Presets:</span>
        {PROMPT_PRESETS.map((preset, idx) => (
          <button
            key={idx}
            type="button"
            disabled={isRunning}
            onClick={() => setMessage(preset)}
            className="rounded-md border border-zinc-800/80 bg-zinc-900/60 px-2.5 py-1 text-[11px] text-zinc-400 hover:border-zinc-700 hover:text-zinc-200 hover:bg-zinc-800/80 transition-all font-mono text-left truncate max-w-xs"
          >
            {preset.slice(0, 36)}...
          </button>
        ))}
      </div>

      {/* Advanced Toggle */}
      <div className="mt-4 border-t border-zinc-800/60 pt-3">
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition-colors font-mono"
          >
            <SlidersHorizontal size={14} />
            <span>Execution Parameters</span>
            {showAdvanced ? <CaretUp size={12} /> : <CaretDown size={12} />}
          </button>

          {/* Primary Action Button */}
          <button
            type="button"
            onClick={handleRun}
            disabled={!message.trim() || isRunning}
            className={cn(
              "flex items-center gap-2 rounded-lg px-5 py-2 text-xs font-semibold uppercase tracking-wider font-mono transition-all active:scale-[0.98]",
              !message.trim() || isRunning
                ? "bg-zinc-800 text-zinc-500 cursor-not-allowed border border-zinc-700/50"
                : "bg-emerald-400 text-zinc-950 hover:bg-emerald-300 shadow-sm border border-emerald-300"
            )}
          >
            {isRunning ? (
              <>
                <CircleNotch size={15} className="animate-spin text-zinc-950" />
                <span>Orchestrating...</span>
              </>
            ) : (
              <>
                <Play size={14} weight="fill" />
                <span>Run</span>
              </>
            )}
          </button>
        </div>

        {/* Collapsible Advanced Parameters */}
        {showAdvanced && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 rounded-lg bg-zinc-950/60 p-3.5 border border-zinc-800/80 text-xs font-mono">
            <label className="flex items-center justify-between gap-2 cursor-pointer">
              <span className="text-zinc-400">Enable Reflection Loop</span>
              <input
                type="checkbox"
                checked={enableReflection}
                onChange={(e) => setEnableReflection(e.target.checked)}
                className="h-4 w-4 rounded-sm border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-emerald-500"
              />
            </label>

            <label className="flex items-center justify-between gap-2 cursor-pointer">
              <span className="text-zinc-400">Enable QA Validation</span>
              <input
                type="checkbox"
                checked={enableQA}
                onChange={(e) => setEnableQA(e.target.checked)}
                className="h-4 w-4 rounded-sm border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-emerald-500"
              />
            </label>

            <div className="flex items-center gap-2">
              <span className="text-zinc-400 whitespace-nowrap">Conv ID:</span>
              <input
                type="text"
                placeholder="optional (e.g. dev-session)"
                value={conversationId}
                onChange={(e) => setConversationId(e.target.value)}
                className="w-full rounded-md border border-zinc-800 bg-zinc-900 px-2 py-1 text-xs text-zinc-200 placeholder-zinc-600 focus:border-emerald-500 focus:outline-hidden"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
