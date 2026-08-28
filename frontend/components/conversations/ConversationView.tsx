"use client";

import { useEffect, useState } from "react";
import {
  ChatCircleDots,
  Plus,
  Trash,
  PaperPlaneRight,
  User,
  Sparkle,
  MagnifyingGlass,
  CircleNotch,
} from "@phosphor-icons/react";
import { api } from "@/lib/api";
import { ConversationMessage } from "@/lib/types";
import { useAppStore } from "@/lib/store";
import { CodeBlock } from "../shared/CodeBlock";
import { EmptyState } from "../shared/EmptyState";

interface ConversationSession {
  id: string;
  title: string;
  updatedAt: string;
  messageCount: number;
}

const INITIAL_SESSIONS: ConversationSession[] = [
  {
    id: "conv-arch-sync",
    title: "DAG Architecture & State Transitions",
    updatedAt: "10 mins ago",
    messageCount: 4,
  },
  {
    id: "conv-perf-audit",
    title: "Qdrant Vector Embedding Analysis",
    updatedAt: "45 mins ago",
    messageCount: 2,
  },
  {
    id: "conv-sec-review",
    title: "API Security & Rate Limiting Audit",
    updatedAt: "2 hours ago",
    messageCount: 3,
  },
];

export function ConversationView() {
  const [sessions, setSessions] = useState<ConversationSession[]>(INITIAL_SESSIONS);
  const [activeSessionId, setActiveSessionId] = useState<string>("conv-arch-sync");
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [search, setSearch] = useState("");

  const { addNotification } = useAppStore();

  useEffect(() => {
    let isMounted = true;
    api.getConversation(activeSessionId).then((data) => {
      if (isMounted) setMessages(data);
    });
    return () => {
      isMounted = false;
    };
  }, [activeSessionId]);

  const handleSendMessage = async () => {
    if (!newMessage.trim() || sending) return;

    const userMsg: ConversationMessage = {
      id: "msg-" + Date.now(),
      role: "user",
      content: newMessage.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setNewMessage("");
    setSending(true);

    try {
      await api.storeConversationMessage(activeSessionId, userMsg);

      // Trigger multi-agent execution response
      const res = await api.executeRequest({
        message: userMsg.content,
        conversation_id: activeSessionId,
      });

      const assistantMsg: ConversationMessage = {
        id: "msg-ast-" + Date.now(),
        role: "assistant",
        content: res.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      await api.storeConversationMessage(activeSessionId, assistantMsg);
    } catch {
      addNotification("error", "Failed to communicate with conversation store");
    } finally {
      setSending(false);
    }
  };

  const handleClear = async () => {
    try {
      await api.clearConversation(activeSessionId);
      setMessages([]);
      addNotification("success", "Conversation thread cleared");
    } catch {
      addNotification("error", "Failed to clear conversation");
    }
  };

  const handleNewSession = () => {
    const newId = "conv-" + Math.random().toString(36).substring(2, 8);
    const newSession: ConversationSession = {
      id: newId,
      title: "New Conversation Thread",
      updatedAt: "Just now",
      messageCount: 0,
    };
    setSessions([newSession, ...sessions]);
    setActiveSessionId(newId);
    setMessages([]);
  };

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(search.toLowerCase()) ||
    s.id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-[600px] h-[calc(100dvh-180px)]">
      {/* Left Column: Session List (4 cols) */}
      <div className="lg:col-span-4 flex flex-col rounded-xl border border-zinc-800 bg-[#0e0e11] overflow-hidden card-shine">
        {/* Session Header */}
        <div className="p-3.5 border-b border-zinc-800/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ChatCircleDots size={16} className="text-emerald-400" />
            <span className="text-xs font-semibold text-zinc-200 font-mono uppercase tracking-wider">
              Threads ({sessions.length})
            </span>
          </div>
          <button
            onClick={handleNewSession}
            className="flex items-center gap-1 rounded-md border border-zinc-700 bg-zinc-800/80 px-2 py-1 text-[11px] text-zinc-200 hover:bg-zinc-700 hover:text-white font-mono transition-all"
          >
            <Plus size={12} weight="bold" />
            <span>New</span>
          </button>
        </div>

        {/* Search */}
        <div className="p-2.5 border-b border-zinc-800/60">
          <div className="relative">
            <MagnifyingGlass
              size={14}
              className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-500"
            />
            <input
              type="text"
              placeholder="Filter threads..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-md border border-zinc-800 bg-zinc-950/80 pl-8 pr-2.5 py-1 text-xs text-zinc-200 placeholder-zinc-500 focus:border-emerald-500 focus:outline-hidden font-mono"
            />
          </div>
        </div>

        {/* List of Sessions */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1.5 divide-y-0">
          {filteredSessions.map((session) => {
            const isActive = session.id === activeSessionId;
            return (
              <div
                key={session.id}
                onClick={() => setActiveSessionId(session.id)}
                className={`cursor-pointer rounded-lg p-3 transition-all font-mono ${
                  isActive
                    ? "bg-zinc-800/90 border border-emerald-500/30 text-zinc-100 shadow-sm"
                    : "hover:bg-zinc-900/60 text-zinc-400 hover:text-zinc-200"
                }`}
              >
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold truncate max-w-[190px]">
                    {session.title}
                  </h4>
                  <span className="text-[10px] text-zinc-500">
                    {session.updatedAt}
                  </span>
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px] text-zinc-500">
                  <span>ID: {session.id}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Column: Chat Stream & Composer (8 cols) */}
      <div className="lg:col-span-8 flex flex-col rounded-xl border border-zinc-800 bg-[#0c0c0e] overflow-hidden card-shine">
        {/* Active Header */}
        <div className="flex items-center justify-between border-b border-zinc-800/80 bg-zinc-900/40 p-3.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-zinc-200 font-mono">
              Thread: {activeSessionId}
            </span>
            <span className="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] text-emerald-400 font-mono">
              Redis Cached
            </span>
          </div>

          <button
            onClick={handleClear}
            className="flex items-center gap-1 text-xs text-zinc-400 hover:text-rose-400 font-mono transition-colors"
          >
            <Trash size={14} />
            <span>Clear</span>
          </button>
        </div>

        {/* Message Viewport */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <EmptyState
              title="Empty Conversation"
              description="Send a message below to start a multi-turn context thread with the autonomous agents."
              icon={<ChatCircleDots size={24} className="text-zinc-500" />}
              className="my-auto h-full"
            />
          ) : (
            messages.map((msg, idx) => {
              const isUser = msg.role === "user";
              return (
                <div
                  key={msg.id || idx}
                  className={`flex gap-3 text-xs font-mono ${
                    isUser ? "justify-end" : "justify-start"
                  }`}
                >
                  {!isUser && (
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-emerald-950/80 border border-emerald-800/60 text-emerald-400">
                      <Sparkle size={14} weight="duotone" />
                    </div>
                  )}

                  <div
                    className={`max-w-xl rounded-xl p-3.5 space-y-1.5 ${
                      isUser
                        ? "bg-zinc-800 text-zinc-100 border border-zinc-700"
                        : "bg-[#141418] text-zinc-200 border border-zinc-800/80"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3 text-[10px] text-zinc-400 pb-1 border-b border-zinc-800/40">
                      <span className="uppercase font-bold tracking-wider">
                        {isUser ? "You" : "Supervisor Agent"}
                      </span>
                      <span>
                        {msg.timestamp
                          ? new Date(msg.timestamp).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : ""}
                      </span>
                    </div>
                    <div className="whitespace-pre-wrap leading-relaxed">
                      {msg.content}
                    </div>
                  </div>

                  {isUser && (
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-zinc-800 border border-zinc-700 text-zinc-300">
                      <User size={14} />
                    </div>
                  )}
                </div>
              );
            })
          )}
          {sending && (
            <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
              <CircleNotch size={14} className="animate-spin text-emerald-400" />
              <span>Agents synthesizing response...</span>
            </div>
          )}
        </div>

        {/* Composer Input */}
        <div className="border-t border-zinc-800/80 bg-zinc-950/80 p-3">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              placeholder="Type message to agents in this thread..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              disabled={sending}
              className="flex-1 rounded-lg border border-zinc-800 bg-zinc-900/90 px-3.5 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:border-emerald-500 focus:outline-hidden font-mono"
            />
            <button
              type="submit"
              disabled={!newMessage.trim() || sending}
              className="flex items-center gap-1.5 rounded-lg bg-emerald-400 px-4 py-2 text-xs font-semibold text-zinc-950 font-mono hover:bg-emerald-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <PaperPlaneRight size={14} weight="fill" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
