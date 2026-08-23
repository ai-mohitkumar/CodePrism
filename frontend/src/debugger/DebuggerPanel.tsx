import React from 'react';
import { 
  Play, 
  RotateCcw, 
  Square, 
  ArrowRight, 
  CornerDownRight, 
  Layers, 
  Eye, 
  CircleDot 
} from 'lucide-react';
import { DebugStepResponse } from '../types';

interface DebuggerPanelProps {
  isDebugging: boolean;
  debugState: DebugStepResponse | null;
  breakpoints: number[];
  onToggleBreakpoint: (line: number) => void;
  onStepOver: () => void;
  onContinue: () => void;
  onStop: () => void;
  onRestart: () => void;
}

export const DebuggerPanel: React.FC<DebuggerPanelProps> = ({
  isDebugging,
  debugState,
  breakpoints,
  onToggleBreakpoint,
  onStepOver,
  onContinue,
  onStop,
  onRestart,
}) => {
  return (
    <div className="w-80 bg-[#0E1322] border-l border-gray-800 flex flex-col h-full select-none shrink-0">
      {/* Debug Header & Controls Bar */}
      <div className="h-10 px-3 border-b border-gray-800/80 bg-[#12182B] flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-300">Debugger</span>
        {/* Debug Action Buttons */}
        <div className="flex items-center gap-1">
          <button
            onClick={onContinue}
            className="p-1 rounded hover:bg-emerald-600/30 text-emerald-400"
            title="Continue (F5)"
          >
            <Play className="w-4 h-4 fill-emerald-400" />
          </button>
          <button
            onClick={onStepOver}
            className="p-1 rounded hover:bg-blue-600/30 text-blue-400"
            title="Step Over (F10)"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={onRestart}
            className="p-1 rounded hover:bg-purple-600/30 text-purple-400"
            title="Restart Debugging"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onStop}
            className="p-1 rounded hover:bg-rose-600/30 text-rose-400"
            title="Stop Debugging"
          >
            <Square className="w-3.5 h-3.5 fill-rose-400 text-rose-400" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-4 text-xs font-mono">
        {/* Variables Watch */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-gray-400 uppercase text-[10px] font-sans font-bold border-b border-gray-800 pb-1">
            <span className="flex items-center gap-1"><Eye className="w-3.5 h-3.5 text-blue-400" /> Variables</span>
          </div>

          {debugState?.variables && Object.keys(debugState.variables).length > 0 ? (
            <div className="border border-gray-800/80 rounded-lg overflow-hidden divide-y divide-gray-800/60 bg-gray-950/40">
              {Object.entries(debugState.variables).map(([name, val]) => (
                <div key={name} className="px-2.5 py-1.5 flex items-center justify-between">
                  <span className="text-blue-300 font-bold">{name}:</span>
                  <span className="text-emerald-400 truncate max-w-[140px]">{JSON.stringify(val)}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-600 italic text-[11px]">No local variables in frame. Click Step Over.</div>
          )}
        </div>

        {/* Call Stack */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-gray-400 uppercase text-[10px] font-sans font-bold border-b border-gray-800 pb-1">
            <span className="flex items-center gap-1"><Layers className="w-3.5 h-3.5 text-indigo-400" /> Call Stack</span>
          </div>
          {debugState?.call_stack ? (
            <div className="space-y-1">
              {debugState.call_stack.map((frame, idx) => (
                <div key={idx} className="p-1.5 rounded bg-gray-900 border border-gray-800 text-[11px] text-gray-300">
                  {frame}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-600 italic text-[11px]">Program idle.</div>
          )}
        </div>

        {/* Breakpoints List */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-gray-400 uppercase text-[10px] font-sans font-bold border-b border-gray-800 pb-1">
            <span className="flex items-center gap-1"><CircleDot className="w-3.5 h-3.5 text-rose-400" /> Breakpoints</span>
            <span className="text-gray-500 font-sans">{breakpoints.length} active</span>
          </div>

          {breakpoints.length > 0 ? (
            <div className="space-y-1">
              {breakpoints.map((line) => (
                <div 
                  key={line} 
                  className="px-2 py-1.5 rounded bg-gray-900/60 border border-gray-800/80 flex items-center justify-between text-[11px]"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                    <span className="text-gray-300">Line {line}</span>
                  </div>
                  <button
                    onClick={() => onToggleBreakpoint(line)}
                    className="text-gray-500 hover:text-rose-400 text-xs"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-600 italic text-[11px]">Click on the editor gutter to set breakpoints.</div>
          )}
        </div>
      </div>
    </div>
  );
};
