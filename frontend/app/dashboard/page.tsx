"use client";

import { useEffect, useState } from "react";
import { RequestComposer } from "@/components/dashboard/RequestComposer";
import { ExecutionLiveCard } from "@/components/dashboard/ExecutionLiveCard";
import { ResponseViewer } from "@/components/dashboard/ResponseViewer";
import { MetricCard } from "@/components/shared/MetricCard";
import { api } from "@/lib/api";
import { SystemMetrics } from "@/lib/types";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { Lightning, Cpu, Clock, CheckCircle } from "@phosphor-icons/react";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);

  useEffect(() => {
    let isMounted = true;
    api.getMetrics().then((data) => {
      if (isMounted) setMetrics(data);
    });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="space-y-6 pb-12">
      {/* Top Metric Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <MetricCard
          label="Total Invocations"
          value={formatNumber(metrics?.total_requests || 148)}
          subtext="97.3% success rate"
          icon={<Lightning size={16} />}
          variant="emerald"
        />
        <MetricCard
          label="Avg Graph Latency"
          value={`${metrics?.average_latency || 1.42}s`}
          subtext="Parallel DAG active"
          icon={<Clock size={16} />}
          variant="sky"
        />
        <MetricCard
          label="Tokens Ingested"
          value={formatNumber(metrics?.total_tokens || 382450)}
          subtext="Nemotron 3 Ultra"
          icon={<Cpu size={16} />}
          variant="default"
        />
        <MetricCard
          label="Cumulative Cost"
          value={formatCurrency(metrics?.total_cost || 0.5736)}
          subtext="OpenRouter billing"
          icon={<CheckCircle size={16} />}
          variant="emerald"
        />
      </div>

      {/* Main Orchestration Workspace */}
      <div className="grid grid-cols-1 gap-6">
        <RequestComposer />
        <ExecutionLiveCard />
        <ResponseViewer />
      </div>
    </div>
  );
}
