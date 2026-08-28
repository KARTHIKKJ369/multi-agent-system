"use client";

import { useEffect, useState } from "react";
import { AgentConfig } from "@/lib/types";
import { api } from "@/lib/api";
import { AgentCard } from "./AgentCard";
import { Skeleton } from "../shared/SkeletonLoader";

export function AgentGrid() {
  const [agents, setAgents] = useState<AgentConfig[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.listAgents().then((data) => {
      if (isMounted) {
        setAgents(data);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-64 rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {agents.map((agent) => (
        <AgentCard key={agent.agent_id} agent={agent} />
      ))}
    </div>
  );
}
