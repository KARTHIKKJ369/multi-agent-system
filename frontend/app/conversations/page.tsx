"use client";

import { ConversationView } from "@/components/conversations/ConversationView";
import { ChatCircleDots } from "@phosphor-icons/react";

export default function ConversationsPage() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <ChatCircleDots size={20} className="text-emerald-400" weight="duotone" />
          <h2 className="text-lg font-bold tracking-tight text-zinc-100 font-mono">
            Conversation State & Memory Threads
          </h2>
        </div>
        <p className="text-xs text-zinc-400 font-mono">
          Explore Redis session context caches, conversation histories, and agent memory state.
        </p>
      </div>

      <ConversationView />
    </div>
  );
}
