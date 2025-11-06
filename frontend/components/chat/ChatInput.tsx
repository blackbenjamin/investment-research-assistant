"use client";

import { useState, KeyboardEvent, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  useReranking?: boolean;
  onRerankingChange?: (value: boolean) => void;
}

export default function ChatInput({ 
  onSend, 
  disabled = false, 
  useReranking = true, 
  onRerankingChange 
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "48px";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "48px";
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex items-end gap-3">
      <div className="flex-1 rounded-lg border border-slate-700 bg-slate-900 shadow-sm focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the financial documents..."
          disabled={disabled}
          rows={1}
          className="w-full resize-none border-0 bg-transparent px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-0"
          style={{
            minHeight: "48px",
            maxHeight: "200px",
          }}
        />
      </div>
      <button
        onClick={handleSubmit}
        disabled={disabled || !message.trim()}
        className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-blue-600 shadow-sm"
      >
        <svg
          className="h-5 w-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
      </button>
      
      {/* Reranking Toggle */}
      {onRerankingChange && (
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer hover:text-slate-300 transition-colors">
            <input
              type="checkbox"
              checked={useReranking}
              onChange={(e) => onRerankingChange(e.target.checked)}
              disabled={disabled}
              className="h-4 w-4 rounded border-slate-600 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            />
            <span>Enable reranking</span>
          </label>
        </div>
      )}
    </div>
  );
}

