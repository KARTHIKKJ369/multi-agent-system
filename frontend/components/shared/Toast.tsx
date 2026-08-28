"use client";

import { useAppStore } from "@/lib/store";
import { CheckCircle, XCircle, Info, Warning, X } from "@phosphor-icons/react";

export function ToastContainer() {
  const { notifications, removeNotification } = useAppStore();

  if (notifications.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {notifications.map((n) => {
        let bgClass = "bg-zinc-900 border-zinc-700 text-zinc-200";
        let Icon = Info;

        if (n.type === "success") {
          bgClass = "bg-emerald-950/90 border-emerald-700/80 text-emerald-200";
          Icon = CheckCircle;
        } else if (n.type === "error") {
          bgClass = "bg-rose-950/90 border-rose-700/80 text-rose-200";
          Icon = XCircle;
        } else if (n.type === "warning") {
          bgClass = "bg-amber-950/90 border-amber-700/80 text-amber-200";
          Icon = Warning;
        }

        return (
          <div
            key={n.id}
            className={`pointer-events-auto flex items-center justify-between gap-3 rounded-xl border p-3.5 shadow-xl text-xs font-mono transition-all animate-in fade-in slide-in-from-bottom-2 ${bgClass}`}
          >
            <div className="flex items-center gap-2.5">
              <Icon size={16} weight="bold" className="shrink-0" />
              <span>{n.message}</span>
            </div>
            <button
              onClick={() => removeNotification(n.id)}
              className="text-zinc-400 hover:text-white p-0.5 rounded"
            >
              <X size={12} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
