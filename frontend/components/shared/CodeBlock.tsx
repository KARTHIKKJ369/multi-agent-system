"use client";

import { useState } from "react";
import { Copy, Check, Terminal } from "@phosphor-icons/react";
import { cn } from "@/lib/utils";

interface CodeBlockProps {
  code: string;
  language?: string;
  title?: string;
  className?: string;
  maxHeight?: string;
}

export function CodeBlock({
  code,
  language = "text",
  title,
  className,
  maxHeight = "max-h-96",
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
  };

  return (
    <div
      className={cn(
        "group relative rounded-xl border border-zinc-800 bg-[#0c0c0e] overflow-hidden text-xs font-mono card-shine",
        className
      )}
    >
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 bg-zinc-900/60 px-4 py-2 text-zinc-400">
        <div className="flex items-center gap-2">
          <Terminal size={14} className="text-zinc-500" />
          <span className="font-semibold text-zinc-300">
            {title || language.toUpperCase()}
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 rounded-md border border-zinc-700/60 bg-zinc-800/80 px-2 py-1 text-[11px] text-zinc-300 hover:bg-zinc-700 hover:text-zinc-100 transition-all active:scale-95"
        >
          {copied ? (
            <>
              <Check size={12} className="text-emerald-400" weight="bold" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy size={12} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code viewport */}
      <pre
        className={cn(
          "overflow-x-auto p-4 leading-relaxed text-zinc-200 selection:bg-emerald-400 selection:text-zinc-950",
          maxHeight
        )}
      >
        <code>{code}</code>
      </pre>
    </div>
  );
}
