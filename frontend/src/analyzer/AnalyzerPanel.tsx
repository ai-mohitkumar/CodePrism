import React, { useState } from 'react';
import { 
  Network, 
  TrendingUp, 
  ShieldCheck, 
  Award, 
  ChevronRight, 
  ChevronDown, 
  FolderTree, 
  CheckCircle2, 
  AlertTriangle 
} from 'lucide-react';
import { ASTResponse, ASTNode, StandardComplexityResult, StandardSecurityResult, StandardQualityResult } from '../types';

interface AnalyzerPanelProps {
  ast: ASTResponse | null | undefined;
  complexity: StandardComplexityResult | null;
  security: StandardSecurityResult | null;
  quality: StandardQualityResult | null;
}

const ASTTreeNode: React.FC<{ node: ASTNode; depth?: number }> = ({ node, depth = 0 }) => {
  const [isOpen, setIsOpen] = useState(depth < 3);
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className="text-xs font-mono">
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-1.5 py-1 px-1.5 rounded hover:bg-gray-800/60 cursor-pointer ${
          node.type === 'FunctionDef' ? 'text-purple-300 font-semibold' :
          node.type === 'For' || node.type === 'While' ? 'text-amber-300 font-semibold' :
          node.type === 'Call' ? 'text-blue-300' : 'text-gray-300'
        }`}
        style={{ paddingLeft: `${depth * 14 + 6}px` }}
      >
        {hasChildren ? (
          isOpen ? <ChevronDown className="w-3.5 h-3.5 text-gray-500 shrink-0" /> : <ChevronRight className="w-3.5 h-3.5 text-gray-500 shrink-0" />
        ) : (
          <span className="w-3.5 h-3.5 inline-block shrink-0" />
        )}
        <span className="truncate">{node.name}</span>
        {node.lineno && (
          <span className="text-[10px] text-gray-600 ml-auto font-sans">L{node.lineno}</span>
        )}
      </div>

      {hasChildren && isOpen && (
        <div className="border-l border-gray-800/60 ml-2">
          {node.children.map((child) => (
            <ASTTreeNode key={child.id} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export const AnalyzerPanel: React.FC<AnalyzerPanelProps> = ({
  ast,
  complexity,
  security,
  quality,
}) => {
  const [activeSection, setActiveSection] = useState<'complexity' | 'ast' | 'security' | 'quality'>('complexity');

  return (
    <div className="w-80 bg-[#0E1322] border-l border-gray-800 flex flex-col h-full select-none shrink-0">
      {/* Analyzer Header Bar */}
      <div className="h-10 px-2 border-b border-gray-800/80 bg-[#12182B] flex items-center gap-1 overflow-x-auto text-xs">
        <button
          onClick={() => setActiveSection('complexity')}
          className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
            activeSection === 'complexity'
              ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Big-O
        </button>
        <button
          onClick={() => setActiveSection('ast')}
          className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
            activeSection === 'ast'
              ? 'bg-purple-600/20 text-purple-400 border border-purple-500/30'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          AST Tree
        </button>
        <button
          onClick={() => setActiveSection('quality')}
          className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
            activeSection === 'quality'
              ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Quality
        </button>
        <button
          onClick={() => setActiveSection('security')}
          className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
            activeSection === 'security'
              ? 'bg-rose-600/20 text-rose-400 border border-rose-500/30'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Security
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {/* Complexity Tab */}
        {activeSection === 'complexity' && (
          <div className="space-y-4 font-sans text-xs">
            {complexity ? (
              <>
                <div className="p-3.5 rounded-xl bg-gradient-to-br from-blue-950/40 to-gray-900 border border-blue-500/30">
                  <span className="text-[10px] uppercase font-bold text-blue-400">Static Time Complexity</span>
                  <div className="text-2xl font-extrabold text-white font-mono my-1">{complexity.time}</div>
                  <div className="flex items-center justify-between text-[11px] text-gray-400 pt-1 border-t border-gray-800">
                    <span>Confidence Score:</span>
                    <span className="font-mono font-bold text-blue-300">{(complexity.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-gray-900/60 border border-gray-800 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-gray-400">Auxiliary Space</span>
                  <div className="text-lg font-bold text-indigo-300 font-mono">{complexity.space}</div>
                </div>

                <div className="p-3 rounded-lg bg-gray-900/60 border border-gray-800 space-y-1.5">
                  <span className="text-[10px] uppercase font-bold text-gray-400">Algorithmic Reasoning</span>
                  <p className="text-gray-300 leading-relaxed text-xs">{complexity.reason}</p>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/60 border border-gray-800/80 grid grid-cols-2 gap-2 text-center text-xs">
                  <div>
                    <span className="text-[10px] text-gray-500 block">Loop Depth</span>
                    <span className="font-mono font-bold text-white">{complexity.nested_depth} Level{complexity.nested_depth === 1 ? '' : 's'}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-500 block">Halving Search</span>
                    <span className="font-mono font-bold text-blue-400">{complexity.has_halving ? 'Yes' : 'No'}</span>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-gray-500 italic text-center p-4">Click Analyze to evaluate Big-O complexity.</div>
            )}
          </div>
        )}

        {/* AST Tree Visualizer */}
        {activeSection === 'ast' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-gray-400 font-semibold border-b border-gray-800 pb-1.5">
              <span className="flex items-center gap-1.5"><FolderTree className="w-3.5 h-3.5 text-purple-400" /> AST Hierarchy</span>
            </div>

            {ast?.root ? (
              <div className="border border-gray-800 rounded-lg p-2 bg-gray-950/60 overflow-x-auto">
                <ASTTreeNode node={ast.root} depth={0} />
              </div>
            ) : (
              <div className="text-gray-500 italic text-center p-4 text-xs">No AST parsed yet. Click Analyze.</div>
            )}

            {ast?.summary && (
              <div className="space-y-1 pt-1 text-xs text-gray-400">
                {ast.summary.map((s, idx) => (
                  <div key={idx} className="flex items-start gap-1.5 text-[11px]">
                    <CheckCircle2 className="w-3 h-3 text-purple-400 shrink-0 mt-0.5" />
                    <span>{s}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Quality Tab */}
        {activeSection === 'quality' && (
          <div className="space-y-3 text-xs">
            {quality ? (
              <>
                <div className="p-3 rounded-lg bg-gray-900 border border-gray-800 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] text-gray-400 uppercase font-bold block">Maintainability</span>
                    <span className="text-xl font-bold text-emerald-400 font-mono">{quality.maintainability}/10</span>
                  </div>
                  <Award className="w-6 h-6 text-emerald-400 opacity-80" />
                </div>
                <div className="p-3 rounded-lg bg-gray-900 border border-gray-800">
                  <span className="text-[10px] text-gray-400 uppercase font-bold block">Cyclomatic Complexity</span>
                  <span className="text-xl font-bold text-blue-400 font-mono">{quality.cyclomatic}</span>
                </div>
              </>
            ) : (
              <div className="text-gray-500 italic text-center p-4">Click Analyze to evaluate code quality.</div>
            )}
          </div>
        )}

        {/* Security Tab */}
        {activeSection === 'security' && (
          <div className="space-y-3 text-xs">
            {security && security.issues && security.issues.length > 0 ? (
              security.issues.map((sec, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/30 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-rose-300">{sec.title}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-500 text-white uppercase">{sec.severity}</span>
                  </div>
                  <p className="text-gray-300 text-[11px]">{sec.description}</p>
                </div>
              ))
            ) : (
              <div className="text-emerald-400 text-center p-4 font-medium flex flex-col items-center gap-2">
                <ShieldCheck className="w-8 h-8 text-emerald-400" />
                <span>Zero Security Vulnerabilities</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
