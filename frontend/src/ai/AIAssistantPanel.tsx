import React, { useState } from 'react';
import { 
  Sparkles, 
  HelpCircle, 
  Bug, 
  Zap, 
  TestTube2, 
  Wrench, 
  ShieldCheck, 
  Copy, 
  Check, 
  Send 
} from 'lucide-react';
import { AIResponse } from '../types';

interface AIAssistantPanelProps {
  onAskAI: (promptType: string, query?: string) => void;
  aiResponse: AIResponse | null;
  isLoading: boolean;
  onApplyCode: (code: string) => void;
}

export const AIAssistantPanel: React.FC<AIAssistantPanelProps> = ({
  onAskAI,
  aiResponse,
  isLoading,
  onApplyCode,
}) => {
  const [query, setQuery] = useState('');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (aiResponse?.code_snippet) {
      navigator.clipboard.writeText(aiResponse.code_snippet);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onAskAI('custom', query);
      setQuery('');
    }
  };

  return (
    <div className="w-80 bg-[#0E1322] border-l border-gray-800 flex flex-col h-full select-none shrink-0">
      {/* AI Header */}
      <div className="h-10 px-3 border-b border-gray-800/80 bg-[#12182B] flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold text-purple-300">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span>AI Assistant</span>
        </div>
      </div>

      {/* Quick Action Pills Grid */}
      <div className="p-2 border-b border-gray-800 grid grid-cols-3 gap-1.5 text-[11px] font-sans">
        <button
          onClick={() => onAskAI('explain')}
          className="p-1.5 rounded bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 flex items-center justify-center gap-1 transition-colors"
        >
          <HelpCircle className="w-3 h-3 text-blue-400" />
          <span>Explain</span>
        </button>

        <button
          onClick={() => onAskAI('debug')}
          className="p-1.5 rounded bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 flex items-center justify-center gap-1 transition-colors"
        >
          <Bug className="w-3 h-3 text-rose-400" />
          <span>Debug</span>
        </button>

        <button
          onClick={() => onAskAI('optimize')}
          className="p-1.5 rounded bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 flex items-center justify-center gap-1 transition-colors"
        >
          <Zap className="w-3 h-3 text-yellow-400" />
          <span>Optimize</span>
        </button>

        <button
          onClick={() => onAskAI('complexity')}
          className="p-1.5 rounded bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 flex items-center justify-center gap-1 transition-colors"
        >
          <span>Big-O Why</span>
        </button>

        <button
          onClick={() => onAskAI('tests')}
          className="p-1.5 rounded bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 flex items-center justify-center gap-1 transition-colors"
        >
          <TestTube2 className="w-3 h-3 text-emerald-400" />
          <span>Tests</span>
        </button>

        <button
          onClick={() => onAskAI('refactor')}
          className="p-1.5 rounded bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 flex items-center justify-center gap-1 transition-colors"
        >
          <Wrench className="w-3 h-3 text-cyan-400" />
          <span>Refactor</span>
        </button>
      </div>

      {/* Response Area */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3 font-sans text-xs">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-48 text-center text-gray-400 space-y-2">
            <div className="w-6 h-6 border-2 border-purple-500/20 border-t-purple-500 rounded-full animate-spin"></div>
            <span className="text-xs">Reasoning over code...</span>
          </div>
        ) : aiResponse ? (
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-gradient-to-br from-purple-950/30 to-gray-900 border border-purple-500/30 space-y-1.5">
              <span className="text-[10px] font-bold uppercase text-purple-400">{aiResponse.title}</span>
              <p className="text-gray-200 leading-relaxed text-xs">{aiResponse.content}</p>
            </div>

            {aiResponse.bullet_points && aiResponse.bullet_points.length > 0 && (
              <div className="space-y-1.5">
                {aiResponse.bullet_points.map((pt, idx) => (
                  <div key={idx} className="flex items-start gap-1.5 text-gray-300 text-[11px]">
                    <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-1 shrink-0" />
                    <span>{pt}</span>
                  </div>
                ))}
              </div>
            )}

            {aiResponse.code_snippet && (
              <div className="rounded-lg border border-gray-800 bg-gray-950/80 overflow-hidden font-mono text-xs">
                <div className="px-2.5 py-1 bg-[#12182B] flex items-center justify-between text-[11px] text-gray-400">
                  <span>Suggested Code</span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleCopy}
                      className="hover:text-white p-0.5"
                    >
                      {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    </button>
                    <button
                      onClick={() => onApplyCode(aiResponse.code_snippet!)}
                      className="px-2 py-0.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-sans font-medium"
                    >
                      Apply
                    </button>
                  </div>
                </div>
                <pre className="p-2.5 overflow-x-auto text-gray-200 text-[11px]">{aiResponse.code_snippet}</pre>
              </div>
            )}
          </div>
        ) : (
          <div className="text-gray-500 italic text-center p-6 text-xs">
            Select a quick action above or type a question below to analyze your code with AI.
          </div>
        )}
      </div>

      {/* Bottom Chat Prompt Input */}
      <form onSubmit={handleSubmit} className="p-2 border-t border-gray-800 flex items-center gap-1.5">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask AI about this code..."
          className="flex-1 bg-gray-900 border border-gray-800 text-xs px-2.5 py-1.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-purple-500 text-gray-200"
        />
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="p-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white disabled:opacity-40"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};
