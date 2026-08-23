import React from 'react';
import { 
  Play, 
  Bug, 
  Cpu, 
  Zap, 
  Upload, 
  Layers, 
  ChevronDown, 
  Smartphone, 
  Folder,
  GitBranch,
  History,
  Check,
  Loader2
} from 'lucide-react';
import { LanguageMeta } from '../types';
import { PWAInstallButton } from './PWAInstallButton';

interface TopBarProps {
  language: string;
  languages: LanguageMeta[];
  onLanguageChange: (lang: string) => void;
  onLoadPreset: (presetKey: string) => void;
  onCompile: () => void;
  onRun: () => void;
  onDebug: () => void;
  onAnalyze: () => void;
  onOpenUpload: (tab?: 'single' | 'project' | 'github') => void;
  onToggleMobileView: () => void;
  onSaveCloudProject: () => void;
  onOpenHistory: () => void;
  autosaveStatus?: 'synced' | 'saving' | 'unsaved';
  isLoading: boolean;
  isBackendConnected: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  language,
  languages,
  onLanguageChange,
  onLoadPreset,
  onCompile,
  onRun,
  onDebug,
  onAnalyze,
  onOpenUpload,
  onToggleMobileView,
  onSaveCloudProject,
  onOpenHistory,
  autosaveStatus = 'synced',
  isLoading,
  isBackendConnected,
}) => {
  return (
    <header className="h-14 border-b border-gray-800 bg-[#0E1322] px-3 flex items-center justify-between sticky top-0 z-40 select-none">
      {/* Brand & Autosave Badge */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-600 via-blue-600 to-purple-600 flex items-center justify-center shadow-md shadow-blue-500/20">
          <Layers className="w-4 h-4 text-white" />
        </div>
        <div className="flex items-center gap-2">
          <span className="font-bold text-base tracking-tight bg-gradient-to-r from-emerald-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            CodePrism 🔮
          </span>
          {/* Autosave Status Indicator */}
          <div className="hidden lg:flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-gray-900 border border-gray-800 text-[11px] font-mono text-gray-400">
            {autosaveStatus === 'saving' ? (
              <>
                <Loader2 className="w-3 h-3 text-amber-400 animate-spin" />
                <span className="text-amber-300">Saving...</span>
              </>
            ) : autosaveStatus === 'synced' ? (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                <span className="text-emerald-300">Synced ✓</span>
              </>
            ) : (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-gray-500"></span>
                <span className="text-gray-400">Unsaved</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Main Execution, Compile, Debug, Analyze, Upload, History & Cloud Controls */}
      <div className="flex items-center gap-1.5 md:gap-2">
        {/* Compile Button */}
        <button
          onClick={onCompile}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/40 border border-emerald-500/40 text-emerald-300 text-xs font-semibold shadow-sm transition-all active:scale-95 disabled:opacity-50"
          title="Compile source code & generate target binary/bytecode"
        >
          <Cpu className="w-3.5 h-3.5 text-emerald-400" />
          <span>Compile</span>
        </button>

        {/* Run Button */}
        <button
          onClick={onRun}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-sm transition-all active:scale-95 disabled:opacity-50"
          title="Run Program in Sandbox (Ctrl+Enter / F5)"
        >
          <Play className="w-3.5 h-3.5 fill-white" />
          <span>▶ Run</span>
        </button>

        {/* Debug Button */}
        <button
          onClick={onDebug}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 border border-indigo-500/40 text-indigo-200 text-xs font-semibold shadow-sm transition-all active:scale-95 disabled:opacity-50"
          title="Start Step Debugger"
        >
          <Bug className="w-3.5 h-3.5 text-indigo-400" />
          <span>Debug</span>
        </button>

        {/* Full Analysis Button */}
        <button
          onClick={onAnalyze}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/40 text-purple-200 text-xs font-semibold shadow-sm transition-all active:scale-95 disabled:opacity-50"
          title="Open Full Analysis Workspace (AST, Big-O Complexity & Security)"
        >
          <Zap className="w-3.5 h-3.5 text-purple-400 fill-purple-400" />
          <span>Analyze</span>
        </button>

        {/* Upload Button */}
        <button
          onClick={() => onOpenUpload('single')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/40 border border-blue-500/40 text-blue-300 text-xs font-semibold shadow-sm transition-all active:scale-95"
          title="Upload file or ZIP project for automated compilation & analysis"
        >
          <Upload className="w-3.5 h-3.5 text-blue-400" />
          <span>Upload</span>
        </button>

        {/* Version History & Templates Hub Button */}
        <button
          onClick={onOpenHistory}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-200 text-xs font-semibold shadow-sm transition-all active:scale-95"
          title="Open Project Version History Snapshots, Templates & Share Hub"
        >
          <History className="w-3.5 h-3.5 text-blue-400" />
          <span>History</span>
        </button>

        {/* Save Cloud Project Button */}
        <button
          onClick={onSaveCloudProject}
          className="hidden xl:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-200 text-xs font-semibold shadow-sm transition-all active:scale-95"
          title="Save project snapshot to cloud for multi-device sync"
        >
          <Folder className="w-3.5 h-3.5 text-emerald-400" />
          <span>Save Cloud</span>
        </button>

        {/* Git Button */}
        <button
          onClick={() => onOpenUpload('github')}
          className="hidden 2xl:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 text-xs font-semibold shadow-sm transition-all"
          title="Clone & analyze public GitHub repository"
        >
          <GitBranch className="w-3.5 h-3.5 text-gray-300" />
          <span>Git</span>
        </button>
      </div>

      {/* Language, Dual Install & Mode Controls */}
      <div className="flex items-center gap-2">
        {/* Dedicated PC Install Icon Button */}
        <div className="hidden sm:block">
          <PWAInstallButton mode="pc" />
        </div>

        {/* Dedicated Mobile Install Button */}
        <div className="hidden md:block">
          <PWAInstallButton mode="mobile" />
        </div>

        {/* Dynamic Universal Language Select */}
        <div className="relative">
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="bg-gray-800/90 border border-gray-700 text-gray-200 text-xs font-medium rounded-lg px-2.5 py-1.5 pr-7 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer appearance-none max-w-[150px] truncate"
          >
            {languages && languages.length > 0 ? (
              languages.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.icon} {l.name}
                </option>
              ))
            ) : (
              <>
                <option value="python">🐍 Python 3.12</option>
                <option value="cpp">⚡ C++ (GCC)</option>
                <option value="java">☕ Java (JDK 25)</option>
                <option value="javascript">🌐 JavaScript (Node)</option>
                <option value="typescript">🔷 TypeScript</option>
                <option value="csharp">🟣 C# (.NET 9)</option>
                <option value="rust">🦀 Rust</option>
                <option value="go">🐹 Go</option>
                <option value="sql">🗄️ SQL</option>
              </>
            )}
          </select>
          <ChevronDown className="w-3.5 h-3.5 text-gray-400 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>

        {/* Mobile View Simulator Button */}
        <button
          onClick={onToggleMobileView}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-purple-600/20 hover:bg-purple-600/40 border border-purple-500/40 text-purple-300 text-xs font-semibold shadow-sm transition-all"
          title="Switch to Mobile View (iOS / Android Layout)"
        >
          <Smartphone className="w-3.5 h-3.5 text-purple-400" />
          <span className="hidden sm:inline">Mobile UI</span>
        </button>

        {/* Backend status dot */}
        <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-gray-900 border border-gray-800 text-[11px] font-mono">
          <span className={`w-2 h-2 rounded-full ${isBackendConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></span>
          <span className="hidden 2xl:inline text-gray-400">{isBackendConnected ? 'Online' : 'Offline'}</span>
        </div>
      </div>
    </header>
  );
};
