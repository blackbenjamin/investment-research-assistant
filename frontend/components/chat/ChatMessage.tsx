"use client";

import { useState } from "react";
import { Message, Source } from "../../types";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gradient-to-br from-blue-500 to-indigo-600 text-white"
        }`}
      >
        {isUser ? (
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
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
        ) : (
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? "text-right" : ""}`}>
        <div
          className={`inline-block rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-blue-600 text-white"
              : "bg-slate-800 border border-slate-700 text-slate-100 shadow-sm"
          }`}
        >
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        </div>

        {/* Sources for assistant messages */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              Sources ({message.sources.length})
            </div>
            <div className="space-y-2">
              {message.sources.map((source, index) => (
                <SourceCard key={index} source={source} index={index} />
              ))}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <div className={`mt-2 text-xs text-slate-500 ${isUser ? "text-right" : ""}`}>
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
}

interface SourceCardProps {
  source: Source;
  index: number;
}

function SourceCard({ source, index }: SourceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/50 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 text-left hover:bg-slate-800 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-500/20 text-xs font-semibold text-blue-400 border border-blue-500/30">
              {index + 1}
            </div>
            <div>
              <div className="font-semibold text-slate-200">
                {source.document_name}
              </div>
              <div className="text-xs text-slate-400">
                Page {source.page_number} • Relevance: {(source.score * 100).toFixed(1)}%
              </div>
            </div>
          </div>
          <svg
            className={`h-5 w-5 text-slate-500 transition-transform ${
              isExpanded ? "rotate-180" : ""
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </button>

      {isExpanded && (
        <div className="border-t border-slate-700 bg-slate-900 px-4 py-3">
          <p className="text-sm text-slate-300 leading-relaxed">{source.text}</p>
        </div>
      )}
    </div>
  );
}

