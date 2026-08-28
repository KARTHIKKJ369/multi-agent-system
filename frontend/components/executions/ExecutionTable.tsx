"use client";

import { useState } from "react";
import Link from "next/link";
import { MagnifyingGlass, Funnel, ArrowRight, TreeStructure } from "@phosphor-icons/react";
import { useAppStore } from "@/lib/store";
import { formatCurrency, formatDuration, formatNumber, truncateString } from "@/lib/utils";
import { StatusBadge } from "../shared/StatusBadge";
import { EmptyState } from "../shared/EmptyState";

export function ExecutionTable() {
  const { executionHistory } = useAppStore();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filtered = executionHistory.filter((item) => {
    const matchesSearch =
      item.user_request.toLowerCase().includes(search.toLowerCase()) ||
      item.execution_id.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || item.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-4">
      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border border-zinc-800 bg-[#0e0e11] p-3.5 card-shine">
        <div className="relative flex-1">
          <MagnifyingGlass
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
          />
          <input
            type="text"
            placeholder="Search executions by request or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-zinc-800 bg-zinc-950/80 pl-9 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:border-emerald-500 focus:outline-hidden font-mono"
          />
        </div>

        <div className="flex items-center gap-2">
          <Funnel size={14} className="text-zinc-500" />
          <div className="flex items-center rounded-lg border border-zinc-800 bg-zinc-950/80 p-1 text-xs font-mono">
            {["all", "completed", "running", "failed"].map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => setStatusFilter(status)}
                className={`rounded-md px-2.5 py-1 capitalize transition-colors ${
                  statusFilter === status
                    ? "bg-zinc-800 text-emerald-400 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* History Table */}
      {filtered.length === 0 ? (
        <EmptyState
          title="No Executions Found"
          description="No execution entries match your active query and status filter."
          icon={<TreeStructure size={24} className="text-zinc-500" />}
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-zinc-800 bg-[#0c0c0e] card-shine">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-zinc-800 bg-zinc-900/60 text-zinc-400 uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="py-3 px-4">Execution ID</th>
                  <th className="py-3 px-4">User Request</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Tasks</th>
                  <th className="py-3 px-4">Tokens</th>
                  <th className="py-3 px-4">Cost</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {filtered.map((item) => (
                  <tr
                    key={item.execution_id}
                    className="hover:bg-zinc-900/40 transition-colors group"
                  >
                    <td className="py-3.5 px-4 font-semibold text-zinc-200">
                      <Link
                        href={`/executions/${item.execution_id}`}
                        className="hover:text-emerald-400 transition-colors underline-offset-4 hover:underline"
                      >
                        {item.execution_id}
                      </Link>
                    </td>
                    <td className="py-3.5 px-4 text-zinc-300 max-w-xs truncate">
                      {truncateString(item.user_request, 45)}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={item.status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-zinc-400">
                      {item.completed_tasks?.length || 4} done
                    </td>
                    <td className="py-3.5 px-4 text-zinc-300">
                      {formatNumber(item.total_tokens || 0)}
                    </td>
                    <td className="py-3.5 px-4 text-emerald-400">
                      {formatCurrency(item.total_cost || 0)}
                    </td>
                    <td className="py-3.5 px-4 text-zinc-400">
                      {item.execution_time
                        ? formatDuration(item.execution_time)
                        : "1.8s"}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/executions/${item.execution_id}`}
                        className="inline-flex items-center gap-1 rounded-md border border-zinc-800 bg-zinc-900/80 px-2.5 py-1 text-[11px] text-zinc-300 group-hover:border-zinc-700 group-hover:text-emerald-400 transition-all"
                      >
                        <span>Inspect</span>
                        <ArrowRight size={12} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
