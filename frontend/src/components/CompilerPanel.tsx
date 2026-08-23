import React, { useState } from 'react';
import { 
  Cpu, 
  CheckCircle2, 
  AlertTriangle, 
  Binary, 
  Settings2, 
  FileCode, 
  Clock, 
  Copy, 
  Check, 
  ShieldCheck 
} from 'lucide-react';
import { CompileResponse } from '../types';

interface CompilerPanelProps {
  compileData: CompileResponse | null;
  isLoading: boolean;
  onRecompile: (flags: string[]) => void;
}

export const CompilerPanel: React.FC<CompilerPanelProps> = ({
  compileData,
  isLoading,
  onRecompile,
}) => {
  const [selectedFlag, setSelectedFlag] = useState<string>('-O2');
  const [copied, setCopied] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'status' | 'bytecode'>('status');

  const handleCopyBytecode = () => {
    if (compileData?.ir_bytecode) {
      navigator.clipboard.writeText(compileData.ir_bytecode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="w-80 bg-[#0E1322] border-l border-gray-800 flex flex-col h-full select-none shrink-0 font-sans text-xs">
      {/* Header */}
      <div className="h-10 px-3 border-b border-gray-800/80 bg-[#12182B] flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
          <Cpu className="w-4 h-4 text-emerald-400" />
          <span>Compiler Inspector</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setActiveTab('status')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              activeTab === 'status' ? 'bg-emerald-600/20 text-emerald-300 border border-emerald-500/30' : 'text-gray-400'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('bytecode')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              activeTab === 'bytecode' ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30' : 'text-gray-400'
            }`}
          >
            IR / Assembly
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-48 text-center text-gray-400 space-y-2">
            <div className="w-6 h-6 border-2 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin"></div>
            <span className="text-xs">Invoking native compiler & generating target binary...</span>
          </div>
        ) : compileData ? (
          <>
            {activeTab === 'status' && (
              <>
                {/* Status Hero Card */}
                <div className={`p-3.5 rounded-xl border ${
                  compileData.success 
                    ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' 
                    : 'bg-rose-950/20 border-rose-500/30 text-rose-300'
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 font-bold text-sm">
                      {compileData.success ? (
                        <>
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          <span>Compilation Succeeded</span>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="w-4 h-4 text-rose-400" />
                          <span>Compilation Failed</span>
                        </>
                      )}
                    </div>
                    <span className="text-[10px] font-mono opacity-80">{compileData.compilation_time_ms} ms</span>
                  </div>
                  <div className="text-[11px] text-gray-300 mt-2 font-mono">
                    {compileData.compiler_name}
                  </div>
                </div>

                {/* Target Artifact Card */}
                {compileData.target_artifact && (
                  <div className="p-3 rounded-lg bg-gray-900/60 border border-gray-800 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-gray-400 block">Generated Target Artifact</span>
                    <div className="flex items-center justify-between pt-0.5">
                      <span className="font-mono font-bold text-white text-xs">{compileData.target_artifact}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        {compileData.artifact_type}
                      </span>
                    </div>
                  </div>
                )}

                {/* Compiler Diagnostics */}
                {compileData.diagnostics && compileData.diagnostics.length > 0 ? (
                  <div className="space-y-2">
                    <span className="text-[10px] uppercase font-bold text-gray-400 block">Compiler Diagnostics</span>
                    {compileData.diagnostics.map((diag, idx) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-rose-950/30 border border-rose-500/40 space-y-1 font-mono text-[11px]">
                        <div className="flex items-center justify-between text-rose-300 font-bold">
                          <span>{diag.severity.toUpperCase()} (Line {diag.line || 1})</span>
                        </div>
                        <p className="text-gray-200">{diag.message}</p>
                        {diag.pointer && (
                          <pre className="p-2 rounded bg-black/60 text-rose-300 text-[10px] overflow-x-auto whitespace-pre">
                            {diag.pointer}
                          </pre>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 rounded-lg bg-gray-950/40 border border-gray-800 text-center text-gray-400 text-xs">
                    Errors: <span className="font-bold text-emerald-400">0</span> • Warnings: <span className="font-bold text-gray-300">0</span>
                  </div>
                )}

                {/* Compiler Flags Config */}
                <div className="p-3 rounded-lg bg-gray-900/60 border border-gray-800 space-y-2">
                  <div className="flex items-center justify-between text-[10px] uppercase font-bold text-gray-400">
                    <span className="flex items-center gap-1"><Settings2 className="w-3 h-3 text-purple-400" /> Optimization Flags</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    {['-O0', '-O2', '-O3', '-std=c++17'].map((f) => (
                      <button
                        key={f}
                        onClick={() => {
                          setSelectedFlag(f);
                          onRecompile([f]);
                        }}
                        className={`px-2 py-1 rounded text-[10px] font-mono transition-colors ${
                          selectedFlag === f
                            ? 'bg-purple-600 text-white font-bold'
                            : 'bg-gray-800 text-gray-400 hover:text-white'
                        }`}
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}

            {activeTab === 'bytecode' && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-[10px] uppercase font-bold text-gray-400">
                  <span className="flex items-center gap-1"><Binary className="w-3.5 h-3.5 text-purple-400" /> Disassembly / Bytecode</span>
                  <button
                    onClick={handleCopyBytecode}
                    className="p-1 hover:bg-gray-800 rounded text-gray-400 hover:text-white flex items-center gap-1 text-[10px]"
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>Copy</span>
                  </button>
                </div>
                {compileData.ir_bytecode ? (
                  <pre className="p-2.5 rounded-lg bg-black/60 border border-gray-800 text-gray-300 font-mono text-[10px] overflow-x-auto whitespace-pre-wrap max-h-96">
                    {compileData.ir_bytecode}
                  </pre>
                ) : (
                  <div className="text-gray-500 italic text-center p-4">Bytecode / Disassembly not available for this target.</div>
                )}
              </div>
            )}
          </>
        ) : (
          <div className="text-gray-500 italic text-center p-6">
            Click "Compile" to invoke the language toolchain and generate target binaries.
          </div>
        )}
      </div>
    </div>
  );
};
