export type ExecutionStatus = 
  | "pending" 
  | "running" 
  | "completed" 
  | "failed" 
  | "cancelled";

export type TaskStatus = 
  | "pending" 
  | "ready" 
  | "running" 
  | "completed" 
  | "failed" 
  | "skipped";

export interface TaskModel {
  task_id: string;
  name: string;
  description: string;
  agent_type: string;
  status: TaskStatus;
  dependencies: string[];
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  result?: string;
  error?: string | null;
  start_time?: number | null;
  end_time?: number | null;
  execution_time?: number;
  tokens_used?: number;
  cost?: number;
  retry_count?: number;
}

export interface ExecutionModel {
  execution_id: string;
  user_request: string;
  status: ExecutionStatus;
  progress: number;
  completed_tasks: string[];
  failed_tasks: string[];
  tasks?: Record<string, TaskModel> | TaskModel[];
  total_cost: number;
  total_tokens: number;
  execution_time?: number;
  confidence?: number;
  response?: string;
  created_at?: string;
  conversation_id?: string | null;
}

export interface ExecutionResponse {
  execution_id: string;
  response: string;
  execution_time: number;
  tasks_completed: number;
  total_cost: number;
  total_tokens: number;
  confidence: number;
}

export interface ExecutionStatusResponse {
  execution_id: string;
  status: string;
  progress: number;
  completed_tasks: string[];
  failed_tasks: string[];
  total_cost: number;
  total_tokens: number;
}

export interface AgentConfig {
  agent_id: string;
  name: string;
  agent_type: string;
  description: string;
  capabilities: string[];
  tools: string[];
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  model?: string;
  is_active?: boolean;
}

export interface SystemMetrics {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  total_tokens: number;
  total_cost: number;
  average_latency: number;
  agent_invocations: Record<string, number>;
  uptime_seconds?: number;
}

export interface MemoryStats {
  redis_connected: boolean;
  qdrant_connected: boolean;
  postgres_connected?: boolean;
  active_conversations_count: number;
  total_vectors_count: number;
  memory_ttl_seconds: number;
  collections?: string[];
}

export interface ConversationMessage {
  id?: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string | number;
  metadata?: Record<string, any>;
}

export interface HealthCheckResponse {
  status: string;
  app_name: string;
  version: string;
  environment: string;
}
