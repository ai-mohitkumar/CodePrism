import React, { useState } from 'react';
import { 
  X, 
  Zap, 
  AlertTriangle, 
  FolderTree, 
  TrendingUp, 
  ShieldCheck, 
  Award, 
  Clock, 
  HardDrive, 
  Code2, 
  CheckCircle2, 
  Sparkles,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { UniversalResult, ASTNode, FileStats } from '../types';

interface AnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: UniversalResult | null;
  code: string;
  onAskAI: (promptType: string) => void;
  onApplyFix?: (fix: string) => void;
}

const ASTTreeItem: React.FC<{ node: ASTNode; depth?: number }> = ({ node, depth = 0 }) => {
  const [isOpen, setIsOpen] = useState<boolean>(depth < 3);
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className="text-xs font-mono">
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-1.5 py-1 px-2 rounded hover:bg-gray-800/80 cursor-pointer ${
          node.type === 'FunctionDef' ? 'text-purple-300 font-bold' :
          node.type === 'For' || node.type === 'While' ? 'text-amber-300 font-bold' :
          node.type === 'Call' ? 'text-blue-300' : 'text-gray-300'
        }`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
      >
        {hasChildren ? (
          isOpen ? <ChevronDown className="w-3.5 h-3.5 text-gray-500 shrink-0" /> : <ChevronRight className="w-3.5 h-3.5 text-gray-500 shrink-0" />
        ) : (
          <span className="w-3.5 h-3.5 inline-block shrink-0" />
        )}
        <span className="truncate">{node.name}</span>
        {node.lineno && (
          <span className="text-[10px] text-gray-500 ml-auto font-sans">L{node.lineno}</span>
        )}
      </div>

      {hasChildren && isOpen && (
        <div className="border-l border-gray-800 ml-3">
          {node.children.map((child) => (
            <ASTTreeItem key={child.id} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export const AnalysisModal: React.FC<AnalysisModalProps> = ({
  isOpen,
  onClose,
  result,
  code,
  onAskAI,
  onApplyFix,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'errors' | 'ast' | 'big_o' | 'security'>('overview');

  if (!isOpen || !result) return null;

  const lines = code.split('\n');
  const loc = lines.filter(l => l.trim()).length;
  const functionsCount = (code.match(/\b(def|function|void|int|double|bool|fn|func)\s+\w+/g) || []).length;
  const loopsCount = (code.match(/\b(for|while|foreach|loop)\b/g) || []).length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in select-none">
      <div className="w-full max-w-4xl bg-[#0E1322] border border-gray-800 rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        {/* Header Bar */}
        <div className="px-6 py-4 border-b border-gray-800 bg-[#12182B] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-blue-600 flex items-center justify-center shadow-md shadow-purple-500/20">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>CodePrism Analysis Workspace</span>
                <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-mono font-semibold uppercase">
                  {result.language}
                </span>
              </h2>
              <p className="text-xs text-gray-400">Deep AST Decomposition, Static Big-O Inferencing & Security Audit</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 border-b border-gray-800 bg-[#0A0E1A] flex items-center gap-2 overflow-x-auto text-xs font-semibold">
          {[
            { id: 'overview', label: 'Overview', icon: TrendingUp },
            { id: 'errors', label: 'Errors & Fixes', icon: AlertTriangle, badge: !result.compile.success ? '1' : undefined },
            { id: 'ast', label: 'AST Syntax Tree', icon: FolderTree },
            { id: 'big_o', label: 'Big-O Complexity', icon: Zap },
            { id: 'security', label: 'Security & Quality', icon: ShieldCheck },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-3 px-3 flex items-center gap-2 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-gray-400 hover:text-gray-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className="px-1.5 py-0.2 rounded-full bg-rose-500 text-white text-[10px] font-mono">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Tab Content Body */}
        <div className="flex-1 overflow-y-auto p-6 font-sans select-text">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Hero Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="p-4 rounded-xl bg-gradient-to-br from-blue-950/40 to-gray-900 border border-blue-500/30">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-blue-400 block">Time Complexity</span>
                  <div className="text-2xl font-extrabold text-white font-mono my-1">{result.complexity.time}</div>
                  <span className="text-xs text-gray-400">{(result.complexity.confidence * 100).toFixed(0)}% Confidence Score</span>
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-br from-purple-950/40 to-gray-900 border border-purple-500/30">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-purple-400 block">Auxiliary Space</span>
                  <div className="text-2xl font-extrabold text-white font-mono my-1">{result.complexity.space}</div>
                  <span className="text-xs text-gray-400">Static Memory Inferred</span>
                </div>

                <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 block">Execution Runtime</span>
                  <div className="text-2xl font-extrabold text-white font-mono my-1">{result.execution.runtime_ms} ms</div>
                  <span className="text-xs text-gray-400">Peak RAM: {result.execution.memory_mb} MB</span>
                </div>

                <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-amber-400 block">Maintainability</span>
                  <div className="text-2xl font-extrabold text-white font-mono my-1">{result.quality.maintainability}/10</div>
                  <span className="text-xs text-gray-400">Quality Score: {result.quality.score}</span>
                </div>
              </div>

              {/* Code Statistics Table */}
              <div className="p-4 rounded-xl bg-gray-900/60 border border-gray-800 space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Program Structural Metrics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                  <div className="p-3 rounded-lg bg-black/40 border border-gray-800/80">
                    <span className="text-gray-500 text-[11px] block font-sans">Lines of Code (LOC)</span>
                    <span className="text-base font-bold text-white">{loc}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-black/40 border border-gray-800/80">
                    <span className="text-gray-500 text-[11px] block font-sans">Functions</span>
                    <span className="text-base font-bold text-purple-400">{functionsCount}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-black/40 border border-gray-800/80">
                    <span className="text-gray-500 text-[11px] block font-sans">Loops Total</span>
                    <span className="text-base font-bold text-amber-400">{loopsCount}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-black/40 border border-gray-800/80">
                    <span className="text-gray-500 text-[11px] block font-sans">Loop Nesting Depth</span>
                    <span className="text-base font-bold text-blue-400">{result.complexity.nested_depth} Level{result.complexity.nested_depth === 1 ? '' : 's'}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Errors & Quick Fixes Tab */}
          {activeTab === 'errors' && (
            <div className="space-y-4">
              {!result.compile.success ? (
                <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/40 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-rose-300 font-bold text-sm">
                      <AlertTriangle className="w-5 h-5 text-rose-400" />
                      <span>Compilation / Syntax Error Detected (Line {result.compile.error_line || 1}, Col {result.compile.error_column || 1})</span>
                    </div>
                  </div>

                  {result.compile.error_pointer ? (
                    <pre className="p-3 rounded-lg bg-black/80 font-mono text-xs text-rose-300 overflow-x-auto whitespace-pre">
                      {result.compile.error_pointer}
                    </pre>
                  ) : (
                    <pre className="p-3 rounded-lg bg-black/80 font-mono text-xs text-rose-300 whitespace-pre-wrap">
                      {result.compile.compiler_output}
                    </pre>
                  )}

                  {result.compile.suggested_fix && (
                    <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-500/30 flex items-center justify-between gap-3">
                      <div>
                        <span className="text-[11px] font-bold uppercase text-emerald-400 block">Suggested Quick Fix</span>
                        <code className="text-xs font-mono text-emerald-300 bg-black/50 px-2 py-0.5 rounded mt-1 inline-block">
                          {result.compile.suggested_fix}
                        </code>
                      </div>
                      {onApplyFix && (
                        <button
                          onClick={() => {
                            onApplyFix(result.compile.suggested_fix!);
                            onClose();
                          }}
                          className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md transition-colors"
                        >
                          Apply Fix
                        </button>
                      )}
                    </div>
                  )}

                  <div className="flex items-center gap-2 pt-2">
                    <button
                      onClick={() => {
                        onAskAI('explain');
                        onClose();
                      }}
                      className="px-3 py-1.5 rounded-lg bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/40 text-purple-200 text-xs font-semibold flex items-center gap-1.5"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                      <span>Explain Error with AI</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-emerald-300 space-y-2">
                  <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
                  <div className="font-bold text-base">Zero Syntax or Compilation Errors</div>
                  <p className="text-xs text-gray-400">All syntax structures and native compiler toolchains validated cleanly.</p>
                </div>
              )}
            </div>
          )}

          {/* AST Syntax Tree Tab */}
          {activeTab === 'ast' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-gray-900/60 border border-gray-800 space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Abstract Syntax Tree (AST) Hierarchy</h3>
                {result.ast?.root ? (
                  <div className="border border-gray-800 rounded-lg p-3 bg-black/60 overflow-x-auto max-h-96">
                    <ASTTreeItem node={result.ast.root} depth={0} />
                  </div>
                ) : (
                  <div className="text-gray-500 italic p-6 text-center text-xs">AST hierarchy visualizer parsed standard syntax nodes.</div>
                )}
              </div>
            </div>
          )}

          {/* Big-O Complexity Tab */}
          {activeTab === 'big_o' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-gray-900/60 border border-gray-800 space-y-3">
                <span className="text-xs font-bold uppercase tracking-wider text-gray-400 block">Algorithmic Reasoning Engine</span>
                <p className="text-gray-200 text-sm leading-relaxed">{result.complexity.reason}</p>
                
                {result.complexity.details && result.complexity.details.length > 0 && (
                  <div className="space-y-1.5 pt-2 border-t border-gray-800 text-xs">
                    {result.complexity.details.map((d, i) => (
                      <div key={i} className="flex items-center gap-2 text-gray-300 font-mono">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                        <span>{d}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Security & Quality Tab */}
          {activeTab === 'security' && (
            <div className="space-y-4">
              {result.security.issues && result.security.issues.length > 0 ? (
                <div className="space-y-2">
                  {result.security.issues.map((issue, idx) => (
                    <div key={idx} className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-rose-300 text-sm">{issue.title}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500 text-white uppercase">{issue.severity}</span>
                      </div>
                      <p className="text-gray-300 text-xs">{issue.description}</p>
                      <div className="text-xs text-emerald-300 pt-1 font-sans">
                        <span className="font-semibold text-emerald-400">Suggestion: </span>
                        {issue.suggestion}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-emerald-300 space-y-2">
                  <ShieldCheck className="w-10 h-10 text-emerald-400 mx-auto" />
                  <div className="font-bold text-base">Zero Security Vulnerabilities Detected</div>
                  <p className="text-xs text-gray-400">Static code audit verified no dangerous eval(), SQL injection, or unvalidated memory allocations.</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-3 border-t border-gray-800 bg-[#0D1220] flex items-center justify-between">
          <div className="text-xs text-gray-500 font-mono">
            CodePrism Execution & Analysis Engine
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold transition-colors"
          >
            Close Workspace
          </button>
        </div>
      </div>
    </div>
  );
};
