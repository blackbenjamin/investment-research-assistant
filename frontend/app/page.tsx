import ChatInterface from "@/components/chat/ChatInterface";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-900">
      <div className="mx-auto max-w-7xl px-4 py-8">
        {/* Professional Header */}
        <header className="mb-8 border-b border-slate-800 pb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">
                Investment Research Assistant
              </h1>
              <p className="mt-2 text-slate-400">
                AI-powered document analysis for portfolio managers and investors
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-green-500/20 px-3 py-1.5 text-sm font-medium text-green-400 border border-green-500/30">
                <span className="mr-2 inline-block h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                System Ready
              </div>
            </div>
          </div>
        </header>

        {/* Chat Interface */}
        <ChatInterface />
      </div>
    </main>
  );
}

