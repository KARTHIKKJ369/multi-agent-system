import { create } from "zustand";
import { ExecutionModel, ExecutionResponse, TaskModel } from "./types";

interface Notification {
  id: string;
  type: "success" | "error" | "info" | "warning";
  message: string;
  timestamp: number;
}

interface AppState {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // Active Execution
  activeExecution: ExecutionResponse | null;
  activeExecutionTasks: TaskModel[];
  isRunning: boolean;
  currentExecutionId: string | null;
  setActiveExecution: (exec: ExecutionResponse | null) => void;
  setActiveExecutionTasks: (tasks: TaskModel[]) => void;
  setIsRunning: (running: boolean) => void;
  setCurrentExecutionId: (id: string | null) => void;

  // Execution History
  executionHistory: ExecutionModel[];
  addExecutionHistory: (exec: ExecutionModel) => void;

  // Toast notifications
  notifications: Notification[];
  addNotification: (type: Notification["type"], message: string) => void;
  removeNotification: (id: string) => void;
}

const INITIAL_HISTORY: ExecutionModel[] = [
  {
    execution_id: "exec-9a4f21d",
    user_request: "Refactor task state transition validation and add automated retry safeguards.",
    status: "completed",
    progress: 1.0,
    completed_tasks: ["task-01-plan", "task-02-research", "task-03-coding", "task-04-qa"],
    failed_tasks: [],
    total_cost: 0.0038,
    total_tokens: 2540,
    execution_time: 2.14,
    confidence: 0.965,
    created_at: "2026-08-17 19:42:10",
    conversation_id: "conv-arch-sync",
  },
  {
    execution_id: "exec-7c8e9b2",
    user_request: "Analyze memory footprint of vector embedding cache in Qdrant collections.",
    status: "completed",
    progress: 1.0,
    completed_tasks: ["task-01-plan", "task-02-research", "task-03-analytics"],
    failed_tasks: [],
    total_cost: 0.0022,
    total_tokens: 1480,
    execution_time: 1.48,
    confidence: 0.942,
    created_at: "2026-08-17 19:15:33",
    conversation_id: "conv-perf-audit",
  },
  {
    execution_id: "exec-3b1d5e8",
    user_request: "Synthesize API security checklist and check rate limiting configuration.",
    status: "completed",
    progress: 1.0,
    completed_tasks: ["task-01-plan", "task-02-review", "task-03-writing"],
    failed_tasks: [],
    total_cost: 0.0029,
    total_tokens: 1920,
    execution_time: 1.82,
    confidence: 0.98,
    created_at: "2026-08-17 18:40:19",
    conversation_id: "conv-sec-review",
  },
];

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: false,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  activeExecution: null,
  activeExecutionTasks: [],
  isRunning: false,
  currentExecutionId: null,
  setActiveExecution: (exec) => set({ activeExecution: exec }),
  setActiveExecutionTasks: (tasks) => set({ activeExecutionTasks: tasks }),
  setIsRunning: (running) => set({ isRunning: running }),
  setCurrentExecutionId: (id) => set({ currentExecutionId: id }),

  executionHistory: INITIAL_HISTORY,
  addExecutionHistory: (exec) =>
    set((state) => ({
      executionHistory: [exec, ...state.executionHistory.slice(0, 49)],
    })),

  notifications: [],
  addNotification: (type, message) => {
    const id = Math.random().toString(36).substring(2, 9);
    set((state) => ({
      notifications: [...state.notifications, { id, type, message, timestamp: Date.now() }],
    }));
    setTimeout(() => {
      set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id),
      }));
    }, 4000);
  },
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
}));
