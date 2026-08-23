import React from 'react';
import { 
  Files, 
  Bug, 
  Binary, 
  Cpu,
  Sparkles, 
  FolderArchive 
} from 'lucide-react';

export type ActiveSidebarTab = 'files' | 'compiler' | 'debug' | 'ast' | 'ai';

interface SidebarProps {
  activeTab: ActiveSidebarTab;
  onSelectTab: (tab: ActiveSidebarTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  return (
    <aside className="w-12 bg-[#080B12] border-r border-gray-800 flex flex-col items-center py-3 gap-4 select-none shrink-0 z-30">
      {/* File Explorer Tab */}
      <button
        onClick={() => onSelectTab(activeTab === 'files' ? 'files' : 'files')}
        className={`p-2.5 rounded-xl transition-all ${
          activeTab === 'files'
            ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm'
            : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
        }`}
        title="Project Explorer"
      >
        <Files className="w-5 h-5" />
      </button>

      {/* Compiler Inspector Tab */}
      <button
        onClick={() => onSelectTab(activeTab === 'compiler' ? 'files' : 'compiler')}
        className={`p-2.5 rounded-xl transition-all ${
          activeTab === 'compiler'
            ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 shadow-sm'
            : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
        }`}
        title="Compiler Inspector & IR Disassembly"
      >
        <Cpu className="w-5 h-5" />
      </button>

      {/* Interactive Debugger Tab */}
      <button
        onClick={() => onSelectTab(activeTab === 'debug' ? 'files' : 'debug')}
        className={`p-2.5 rounded-xl transition-all ${
          activeTab === 'debug'
            ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-sm'
            : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
        }`}
        title="Step Debugger & Variables Watch"
      >
        <Bug className="w-5 h-5" />
      </button>

      {/* AST & Big-O Analyzer Tab */}
      <button
        onClick={() => onSelectTab(activeTab === 'ast' ? 'files' : 'ast')}
        className={`p-2.5 rounded-xl transition-all ${
          activeTab === 'ast'
            ? 'bg-purple-600/20 text-purple-400 border border-purple-500/30 shadow-sm'
            : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
        }`}
        title="AST Visualizer & Big-O Complexity"
      >
        <Binary className="w-5 h-5" />
      </button>

      {/* AI Assistant Tab */}
      <button
        onClick={() => onSelectTab(activeTab === 'ai' ? 'files' : 'ai')}
        className={`p-2.5 rounded-xl transition-all mt-auto ${
          activeTab === 'ai'
            ? 'bg-gradient-to-tr from-blue-600 to-purple-600 text-white shadow-md shadow-purple-500/20'
            : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
        }`}
        title="AI Assistant (Explain, Optimize, Tests)"
      >
        <Sparkles className="w-5 h-5" />
      </button>
    </aside>
  );
};
