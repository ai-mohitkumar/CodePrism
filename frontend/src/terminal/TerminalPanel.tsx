import React, { useState } from 'react';
import { 
  Terminal, 
  AlertTriangle, 
  Activity, 
  Edit3, 
  Copy, 
  Check, 
  Lightbulb, 
  Clock, 
  Cpu, 
  Sparkles,
  Layers 
} from 'lucide-react';
import { StandardExecutionResult, StandardCompileResult, ErrorDiagnosis } from '../types';

export type TerminalTab = 'output' | 'problems' | 'profiler' | 'stdin';

interface TerminalPanelProps {
  filename?: string;
  execution: StandardExecutionResult | null;
  compile: StandardCompileResult | null;
  diagnosis: ErrorDiagnosis | null;
  stdin: string;
  onStdinChange: (val: string) => void;
  onApplyFix: (fix: string) => void;
  onExplainError?: () => void;
}

export const TerminalPanel: React.FC<TerminalPanelProps> = ({
  filename = 'main.py',
  execution,
  compile,
  diagnosis,
  stdin,
  onStdinChange,
  onApplyFix,
  onExplainError,
}) => {
  const [activeTab, setActiveTab] = useState<TerminalTab>('output');
  const [copied, setCopied] = useState(false);

  const hasCompileError = (compile && !compile.success) || (execution && execution.status === 'compilation_error');
  const hasSyntaxError = diagnosis && diagnosis.has_error;
  const hasProblems = hasCompileError || hasSyntaxError;

  const handleCopy = () => {
    const text = execution?.stdout || execution?.stderr || compile?.compiler_output || 'No output';
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="h-48 border-t border-gray-800 bg-[#080B12] flex flex-col min-h-0 select-none">
      {/* Terminal Tab Bar */}
      <div className="h-8 px-2 bg-[#101524] border-b border-gray-800 flex items-center justify-between text-xs">
        <div className="flex items-center gap-1">
          {/* Output Tab */}
          <button
            onClick={() => setActiveTab('output')}
            className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
              activeTab === 'output'
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Terminal</span>
          </button>

          {/* Problems Tab */}
          <button
            onClick={() => setActiveTab('problems')}
            className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
              activeTab === 'problems'
                ? 'bg-rose-600/20 text-rose-400 border border-rose-500/30'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Problems</span>
            {hasProblems && (
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
            )}
          </button>

          {/* Profiler Tab */}
          <button
            onClick={() => setActiveTab('profiler')}
            className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
              activeTab === 'profiler'
                ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Profiler & Timing</span>
          </button>

          {/* Input (stdin) Tab */}
          <button
            onClick={() => setActiveTab('stdin')}
            className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
              activeTab === 'stdin'
                ? 'bg-purple-600/20 text-purple-400 border border-purple-500/30'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>Input (stdin)</span>
          </button>
        </div>

        {/* Right Quick Metrics */}
        {execution && (
          <div className="flex items-center gap-2 text-[11px] font-mono text-gray-400 pr-2">
            <span>{execution.runtime_ms} ms</span>
            <span>•</span>
            <span>{execution.memory_mb} MB</span>
            <button
              onClick={handleCopy}
              className="p-1 hover:bg-gray-800 rounded text-gray-400 hover:text-white"
              title="Copy Output"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            </button>
          </div>
        )}
      </div>

      {/* Terminal View Body */}
      <div className="flex-1 min-h-0 p-3 overflow-y-auto font-mono text-xs text-gray-200 select-text">
        {/* Output Console Tab */}
        {activeTab === 'output' && (
          <div className="space-y-2">
            {hasProblems ? (
              /* High-Visibility Diagnostic Error Box */
              <div className="p-3 rounded-xl bg-rose-950/30 border border-rose-500/40 space-y-2.5 text-xs">
                <div className="flex items-center justify-between text-rose-300 font-bold">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                    <span>❌ Compilation / Syntax Error</span>
                  </div>
                  <span className="text-[11px] font-mono text-gray-400">
                    {filename} • Line {compile?.error_line || diagnosis?.line || 1}:{compile?.error_column || diagnosis?.column || 1}
                  </span>
                </div>

                {compile?.error_pointer || diagnosis?.pointer ? (
                  <pre className="p-2.5 rounded bg-black/80 font-mono text-xs text-rose-300 whitespace-pre overflow-x-auto border border-rose-900/40">
                    {compile?.error_pointer || diagnosis?.pointer}
                  </pre>
                ) : (
                  <pre className="p-2.5 rounded bg-black/80 font-mono text-xs text-rose-300 whitespace-pre-wrap">
                    {compile?.compiler_output || diagnosis?.message || execution?.stderr}
                  </pre>
                )}

                {(compile?.suggested_fix || diagnosis?.suggested_fix) && (
                  <div className="p-2.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30 flex items-center justify-between gap-3 font-sans">
                    <div className="flex items-center gap-2 text-xs">
                      <Lightbulb className="w-4 h-4 text-emerald-400 shrink-0" />
                      <div>
                        <span className="font-bold text-emerald-400">Quick Fix: </span>
                        <code className="font-mono text-xs text-emerald-300 bg-black/60 px-1.5 py-0.5 rounded">
                          {compile?.suggested_fix || diagnosis?.suggested_fix}
                        </code>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => onApplyFix((compile?.suggested_fix || diagnosis?.suggested_fix)!)}
                        className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-sm transition-colors"
                      >
                        Apply Fix
                      </button>
                      {onExplainError && (
                        <button
                          onClick={onExplainError}
                          className="px-3 py-1 rounded bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/40 text-purple-200 text-xs font-semibold flex items-center gap-1"
                        >
                          <Sparkles className="w-3 h-3 text-purple-400" />
                          <span>Explain</span>
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : execution?.stdout ? (
              <pre className="text-emerald-300 whitespace-pre-wrap font-mono leading-relaxed">{execution.stdout}</pre>
            ) : execution?.stderr ? (
              <pre className="text-rose-400 whitespace-pre-wrap font-mono leading-relaxed">{execution.stderr}</pre>
            ) : (
              <span className="text-gray-600 italic">Program has not been executed yet. Click "Run" or press Ctrl+Enter.</span>
            )}
          </div>
        )}

        {/* Problems & Diagnostic Pointer Tab */}
        {activeTab === 'problems' && (
          <div className="space-y-3">
            {compile && !compile.success ? (
              <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/30 space-y-2">
                <div className="flex items-center justify-between text-xs text-rose-300 font-semibold">
                  <div className="flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                    <span>Compiler Error (Line {compile.error_line || 1})</span>
                  </div>
                  {compile.suggested_fix && (
                    <button
                      onClick={() => onApplyFix(compile.suggested_fix!)}
                      className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-sans text-xs flex items-center gap-1 shadow-sm transition-colors"
                    >
                      <Lightbulb className="w-3.5 h-3.5" />
                      <span>Apply Auto-Fix</span>
                    </button>
                  )}
                </div>

                {compile.error_pointer ? (
                  <pre className="p-2.5 rounded bg-black/60 font-mono text-xs text-rose-300 whitespace-pre overflow-x-auto">
                    {compile.error_pointer}
                  </pre>
                ) : (
                  <pre className="p-2.5 rounded bg-black/60 font-mono text-xs text-rose-300 whitespace-pre-wrap">
                    {compile.compiler_output}
                  </pre>
                )}
              </div>
            ) : diagnosis?.has_error ? (
              <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/30 space-y-2">
                <div className="flex items-center justify-between text-xs text-rose-300 font-semibold">
                  <div className="flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                    <span>{diagnosis.error_type || 'Syntax Error'} (Line {diagnosis.line})</span>
                  </div>
                  {diagnosis.suggested_fix && (
                    <button
                      onClick={() => onApplyFix(diagnosis.suggested_fix!)}
                      className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-sans text-xs flex items-center gap-1 shadow-sm transition-colors"
                    >
                      <Lightbulb className="w-3.5 h-3.5" />
                      <span>Apply Auto-Fix</span>
                    </button>
                  )}
                </div>
                {diagnosis.pointer && (
                  <pre className="p-2.5 rounded bg-black/60 font-mono text-xs text-rose-300 whitespace-pre overflow-x-auto">
                    {diagnosis.pointer}
                  </pre>
                )}
              </div>
            ) : (
              <div className="text-gray-500 italic">No compile or syntax problems detected. Code is clean.</div>
            )}
          </div>
        )}

        {/* Profiler Tab */}
        {activeTab === 'profiler' && (
          <div className="space-y-3">
            {execution ? (
              <>
                <div className="grid grid-cols-3 gap-2 text-xs font-sans">
                  <div className="p-2 rounded bg-gray-900 border border-gray-800">
                    <span className="text-gray-500 block text-[10px]">Execution Time</span>
                    <span className="font-mono font-bold text-white text-sm">{execution.runtime_ms} ms</span>
                  </div>
                  <div className="p-2 rounded bg-gray-900 border border-gray-800">
                    <span className="text-gray-500 block text-[10px]">Peak Memory</span>
                    <span className="font-mono font-bold text-white text-sm">{execution.memory_mb} MB</span>
                  </div>
                  <div className="p-2 rounded bg-gray-900 border border-gray-800">
                    <span className="text-gray-500 block text-[10px]">CPU Usage</span>
                    <span className="font-mono font-bold text-white text-sm">{execution.cpu_percent}%</span>
                  </div>
                </div>

                {execution.functions && execution.functions.length > 0 && (
                  <div className="border border-gray-800 rounded-lg overflow-hidden mt-2">
                    <div className="px-2.5 py-1.5 bg-[#12182B] text-gray-400 text-[11px] font-sans font-bold flex justify-between">
                      <span>Function Timing (cProfile)</span>
                      <span>Cumulative Time</span>
                    </div>
                    <div className="divide-y divide-gray-800/60 font-mono text-xs">
                      {execution.functions.map((fn, idx) => (
                        <div key={idx} className="px-2.5 py-1.5 flex items-center justify-between text-gray-300">
                          <span>{fn.function_name} ({fn.call_count} call{fn.call_count > 1 ? 's' : ''})</span>
                          <span className="text-blue-400 font-bold">{fn.cumtime_ms} ms</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-gray-500 italic">Run code to capture execution timings and memory profiling.</div>
            )}
          </div>
        )}

        {/* Input (stdin) Tab */}
        {activeTab === 'stdin' && (
          <textarea
            value={stdin}
            onChange={(e) => onStdinChange(e.target.value)}
            placeholder="Type standard input (stdin) passed to input() / cin / readline()..."
            className="w-full h-full bg-transparent focus:outline-none resize-none font-mono text-xs text-gray-200 placeholder-gray-600"
          />
        )}
      </div>
    </div>
  );
};
