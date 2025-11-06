"use client";

import { useState, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { Message, Source, DocumentInfo } from "../../types";

interface ChatInterfaceProps {}

export default function ChatInterface({}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);

  // Fetch documents on mount
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const apiKey = process.env.NEXT_PUBLIC_API_KEY || "";
        
        console.log(`[ChatInterface] Fetching documents from: ${apiUrl}/api/v1/documents`);
        
        const headers: HeadersInit = {
          "Content-Type": "application/json",
        };
        
        // Add API key if configured
        if (apiKey) {
          headers["X-API-Key"] = apiKey;
        }
        
        const response = await fetch(`${apiUrl}/api/v1/documents`, {
          method: "GET",
          headers: headers,
        });
        
        console.log(`[ChatInterface] Documents response status: ${response.status}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log(`[ChatInterface] Documents received:`, data);
          setDocuments(data);
        } else {
          const errorText = await response.text();
          console.error("Failed to fetch documents:", response.status, errorText);
        }
      } catch (error) {
        console.error("Error fetching documents:", error);
      } finally {
        setIsLoadingDocuments(false);
      }
    };

    fetchDocuments();
  }, []);

  const handleSendMessage = async (query: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: query,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const apiKey = process.env.NEXT_PUBLIC_API_KEY || "";
      
      console.log(`[ChatInterface] Fetching from: ${apiUrl}/api/v1/query`);
      
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };
      
      // Add API key if configured
      if (apiKey) {
        headers["X-API-Key"] = apiKey;
      }
      
      const response = await fetch(`${apiUrl}/api/v1/query`, {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          query: query,
          top_k: 5,
          use_reranking: false,
        }),
      });

      console.log(`[ChatInterface] Response status: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[ChatInterface] API error: ${response.status} - ${errorText}`);
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log(`[ChatInterface] Response data:`, data);

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("[ChatInterface] Error fetching answer:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Sorry, I encountered an error processing your query. ${error instanceof Error ? error.message : 'Please check the console for details and try again.'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = (filename: string) => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const downloadUrl = `${apiUrl}/api/v1/documents/${encodeURIComponent(filename)}/download`;
    window.open(downloadUrl, "_blank");
  };

  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return "";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="mx-auto max-w-5xl">
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 shadow-lg backdrop-blur">
        {/* Chat Header */}
        <div className="border-b border-slate-700 bg-gradient-to-r from-slate-800 to-slate-900 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">
                Research Assistant
              </h2>
              <p className="text-sm text-slate-400">
                Ask questions about uploaded financial documents
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-xs text-slate-500">
                {messages.length} {messages.length === 1 ? "message" : "messages"}
              </div>
              {/* Documents List */}
              {isLoadingDocuments ? (
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <svg className="h-4 w-4 animate-spin text-blue-400" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Loading documents...
                </div>
              ) : documents.length > 0 ? (
                <div className="group relative">
                  <button className="flex items-center gap-2 text-xs text-slate-400 hover:text-slate-300 transition-colors">
                    <svg className="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    {documents.length} document{documents.length !== 1 ? "s" : ""} loaded
                  </button>
                  {/* Dropdown */}
                  <div className="absolute right-0 top-full mt-2 w-80 rounded-lg border border-slate-700 bg-slate-900 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                    <div className="p-3 border-b border-slate-700">
                      <h3 className="text-sm font-semibold text-white">Available Documents</h3>
                    </div>
                    <div className="max-h-64 overflow-y-auto p-2">
                      {documents.map((doc) => (
                        <div
                          key={doc.name}
                          className="flex items-center justify-between rounded-lg p-2 hover:bg-slate-800 transition-colors"
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <svg className="h-4 w-4 text-red-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                              </svg>
                              <span className="text-sm text-slate-300 truncate">{doc.name}</span>
                            </div>
                            {doc.file_size && (
                              <div className="text-xs text-slate-500 mt-1 ml-6">
                                {formatFileSize(doc.file_size)}
                              </div>
                            )}
                          </div>
                          {doc.status === "available" && (
                            <button
                              onClick={() => handleDownload(doc.name)}
                              className="ml-2 shrink-0 p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-blue-400 transition-colors"
                              title="Download"
                            >
                              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                              </svg>
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <svg className="h-4 w-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  No documents
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <div className="h-[600px] overflow-y-auto px-6 py-4 bg-slate-900/50">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-500/20 border border-blue-500/30">
                  <svg
                    className="h-8 w-8 text-blue-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
                </div>
                <h3 className="mb-2 text-lg font-semibold text-white">
                  Start Your Research
                </h3>
                <p className="mb-6 text-slate-400">
                  Ask questions about Apple's financial documents
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {[
                    "What is Apple's revenue?",
                    "What are Apple's main risks?",
                    "What is Apple's cash position?",
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => handleSendMessage(suggestion)}
                      className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-700 hover:border-slate-600 hover:text-white"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-500/20 border border-blue-500/30">
                    <svg
                      className="h-5 w-5 animate-spin text-blue-400"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <div className="rounded-lg bg-slate-800/50 px-4 py-3 border border-slate-700">
                      <p className="text-slate-400">Analyzing documents...</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-700 bg-slate-800/50 px-6 py-4">
          <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </div>

        {/* Search Method Legend */}
        <div className="border-t border-slate-700 bg-slate-800/30 px-6 py-3">
          <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6 text-xs">
            <span className="text-slate-500 font-medium shrink-0">Search Methods:</span>
            <div className="flex flex-wrap items-center justify-between sm:justify-around gap-4 sm:gap-6 flex-1">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium border bg-purple-500/20 text-purple-400 border-purple-500/30">
                  <span>✨</span>
                  <span>Semantic</span>
                </span>
                <span className="text-slate-500">Conceptual understanding</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium border bg-green-500/20 text-green-400 border-green-500/30">
                  <span>🔍</span>
                  <span>Keyword</span>
                </span>
                <span className="text-slate-500">Exact term matching</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium border bg-orange-500/20 text-orange-400 border-orange-500/30">
                  <span>🔥</span>
                  <span>Hybrid</span>
                </span>
                <span className="text-slate-500">Both methods combined</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

