"use client";

import { useState } from "react";
import { Message, Source } from "../../types";
import { BlockMath } from "react-katex";
import "katex/dist/katex.min.css";

interface ChatMessageProps {
  message: Message;
}

// Helper function to render content with LaTeX support
function renderContentWithMath(content: string) {
  // Split by LaTeX blocks (\[ ... \])
  const parts: (string | JSX.Element)[] = [];
  // Match \[ ... \] blocks, handling multiline content
  const regex = /\\\[([\s\S]*?)\\\]/g;
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = regex.exec(content)) !== null) {
    // Add text before the LaTeX block
    if (match.index > lastIndex) {
      const textBefore = content.substring(lastIndex, match.index);
      if (textBefore.trim()) {
        parts.push(<span key={key++} className="whitespace-pre-wrap">{textBefore}</span>);
      }
    }

    // Add the LaTeX block - preserve whitespace but trim edges
    const latexContent = match[1].trim();
    parts.push(
      <BlockMath key={key++} math={latexContent} />
    );

    lastIndex = regex.lastIndex;
  }

  // Add remaining text after the last LaTeX block
  if (lastIndex < content.length) {
    const textAfter = content.substring(lastIndex);
    if (textAfter.trim()) {
      parts.push(<span key={key++} className="whitespace-pre-wrap">{textAfter}</span>);
    }
  }

  // If no LaTeX blocks found, return original content
  if (parts.length === 0) {
    return <span className="whitespace-pre-wrap">{content}</span>;
  }

  return <>{parts}</>;
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
          <div className="whitespace-pre-wrap leading-relaxed">
            {renderContentWithMath(message.content)}
          </div>
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

  // Get search method indicator
  const getSearchMethodBadge = () => {
    const method = source.search_method || 'semantic';
    const badges = {
      semantic: {
        icon: '✨',
        label: 'Semantic',
        color: 'bg-purple-500/20 text-purple-400 border-purple-500/30'
      },
      keyword: {
        icon: '🔍',
        label: 'Keyword',
        color: 'bg-green-500/20 text-green-400 border-green-500/30'
      },
      hybrid: {
        icon: '🔥',
        label: 'Hybrid',
        color: 'bg-orange-500/20 text-orange-400 border-orange-500/30'
      }
    };

    const badge = badges[method as keyof typeof badges] || badges.semantic;
    
    return (
      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium border ${badge.color}`}>
        <span>{badge.icon}</span>
        <span>{badge.label}</span>
      </span>
    );
  };

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
            <div className="flex-1">
              <div className="font-semibold text-slate-200">
                {source.document_name}
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-xs text-slate-400">
                  Page {source.page_number} • Relevance: {(source.score * 100).toFixed(1)}%
                </span>
                {getSearchMethodBadge()}
                {source.matched_keywords && source.matched_keywords.length > 0 && (
                  <span className="text-xs text-slate-500">
                    • Matched: {source.matched_keywords.slice(0, 2).join(', ')}
                    {source.matched_keywords.length > 2 && '...'}
                  </span>
                )}
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
