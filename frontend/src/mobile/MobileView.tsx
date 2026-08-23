import React, { useState } from 'react';
import { 
  Play, 
  Cpu, 
  Zap, 
  Sparkles, 
  FolderGit2, 
  Terminal, 
  CheckCircle2, 
  AlertTriangle, 
  Monitor, 
  Upload, 
  ChevronDown, 
  Clock, 
  HardDrive, 
  ShieldCheck, 
  Lightbulb, 
  Plus, 
  Folder,
  Bug,
  Code2,
  FileCode,
  Download
} from 'lucide-react';
import { 
  LanguageMeta, UniversalResult, CompileResponse, 
  AIResponse, ProjectMetadata, FileUploadResponse 
} from '../types';
import { PWAInstallButton } from '../components/PWAInstallButton';

interface MobileViewProps {
  language: string;
  languages: LanguageMeta[];
  code: string;
  onCodeChange: (code: string) => void;
  onLanguageChange: (lang: string) => void;
  onCompile: () => void;
  onRun: () => void;
  onAnalyze: () => void;
  onAskAI: (promptType: string) => void;
  onToggleDesktopView: () => void;
  onOpenFileUpload: () => void;
  onApplyFix?: (fix: string) => void;
  compileData: CompileResponse | null;
  universalResult: UniversalResult | null;
  aiResponse: AIResponse | null;
  cloudProjects: ProjectMetadata[];
  onLoadCloudProject: (projectId: string) => void;
  onSaveCloudProject: () => void;
  isLoading: boolean;
}

export const MobileView: React.FC<MobileViewProps> = ({
  language,
  languages,
  code,
  onCodeChange,
  onLanguageChange,
  onCompile,
  onRun,
  onAnalyze,
  onAskAI,
  onToggleDesktopView,
  onOpenFileUpload,
  onApplyFix,
  compileData,
  universalResult,
  aiResponse,
  cloudProjects,
  onLoadCloudProject,
  onSaveCloudProject,
  isLoading,
}) => {
  const [activeBottomNav, setActiveBottomNav] = useState<'code' | 'files' | 'debug' | 'ai' | 'cloud'>('code');

  const lines = code.split('\n');

  const insertSymbol = (sym: string) => {
    onCodeChange(code + sym);
  };

  const hasCompileError = (compileData && !compileData.success) || (universalResult?.compile && !universalResult.compile.success);
  const errorDiagnostic = compileData?.diagnostics?.[0] || universalResult?.compile;

  return (
    <div className="flex flex-col h-screen w-screen bg-[#070A14] text-gray-100 font-sans select-none overflow-hidden">
      {/* Mobile Top App Bar */}
      <header className="h-13 bg-[#0F1424] border-b border-gray-800/80 px-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <span className="font-extrabold text-base tracking-tight bg-gradient-to-r from-emerald-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            CodePrism 🔮
          </span>
          <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
            PWA
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Dynamic Language Selector */}
          <div className="relative">
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="bg-gray-800/90 border border-gray-700 text-xs font-semibold text-gray-200 rounded-lg px-2.5 py-1.5 pr-6 appearance-none focus:outline-none max-w-[130px] truncate"
            >
              {languages.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.icon} {l.name}
                </option>
              ))}
            </select>
            <ChevronDown className="w-3 h-3 text-gray-400 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          {/* Desktop Switcher */}
          <button
            onClick={onToggleDesktopView}
            className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700"
            title="Switch to PC/Desktop IDE View"
          >
            <Monitor className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-h-0 overflow-y-auto">
        {/* Main Code Tab */}
        {activeBottomNav === 'code' && (
          <div className="flex-1 flex flex-col min-h-0">
            {/* Quick Touch Symbols Bar */}
            <div className="h-8 bg-[#090D18] border-b border-gray-800/80 px-2 flex items-center gap-1.5 overflow-x-auto text-xs shrink-0">
              {['(', ')', '{', '}', '[', ']', ':', '=', ';', '"', '+', '-', '*', '/', 'def', 'return', 'print'].map((sym) => (
                <button
                  key={sym}
                  onClick={() => insertSymbol(sym)}
                  className="px-2 py-0.5 rounded bg-gray-800/80 hover:bg-gray-700 active:bg-blue-600 text-gray-200 font-mono text-[11px] shrink-0 border border-gray-700/50"
                >
                  {sym}
                </button>
              ))}
            </div>

            {/* Mobile Code Editor View */}
            <div className="h-56 min-h-[180px] flex bg-[#0B0F1C] border-b border-gray-800 overflow-hidden">
              <div className="w-9 py-2 bg-[#080B14] border-r border-gray-800/60 text-right pr-2 text-gray-600 font-mono text-xs select-none overflow-hidden">
                {lines.map((_, i) => (
                  <div key={i} className="leading-6">{i + 1}</div>
                ))}
              </div>
              <textarea
                value={code}
                onChange={(e) => onCodeChange(e.target.value)}
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck="false"
                className="flex-1 p-2.5 bg-transparent text-gray-100 font-mono text-xs leading-6 resize-none focus:outline-none select-text whitespace-pre overflow-auto"
                placeholder="Write or paste your code here..."
              />
            </div>

            {/* Core Action Buttons Bar */}
            <div className="p-2.5 bg-[#0D1222] border-b border-gray-800 flex items-center gap-2 shrink-0">
              <button
                onClick={onRun}
                disabled={isLoading}
                className="flex-1 py-2 rounded-xl bg-emerald-600 active:bg-emerald-500 text-white font-bold text-xs shadow-md flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-white" />
                <span>▶ Run</span>
              </button>

              <button
                onClick={onCompile}
                disabled={isLoading}
                className="flex-1 py-2 rounded-xl bg-emerald-600/20 active:bg-emerald-600/40 border border-emerald-500/40 text-emerald-300 font-bold text-xs flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
              >
                <Cpu className="w-3.5 h-3.5 text-emerald-400" />
                <span>Compile</span>
              </button>

              <button
                onClick={onAnalyze}
                disabled={isLoading}
                className="flex-1 py-2 rounded-xl bg-purple-600/20 active:bg-purple-600/40 border border-purple-500/40 text-purple-300 font-bold text-xs flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
              >
                <Zap className="w-3.5 h-3.5 text-purple-400" />
                <span>Analyze</span>
              </button>
            </div>

            {/* Live Output & Diagnostics Area */}
            <div className="flex-1 p-3 space-y-3 font-mono text-xs overflow-y-auto">
              {/* Output Section */}
              <div className="p-3 rounded-xl bg-black/60 border border-gray-800/80 space-y-2">
                <div className="flex items-center justify-between text-[11px] text-gray-400 border-b border-gray-800/60 pb-1.5">
                  <span className="font-bold flex items-center gap-1.5 text-gray-200">
                    <Terminal className="w-3.5 h-3.5 text-emerald-400" /> Output Terminal
                  </span>
                  {universalResult?.execution && (
                    <span>{universalResult.execution.runtime_ms} ms • {universalResult.execution.memory_mb} MB</span>
                  )}
                </div>

                {hasCompileError ? (
                  <div className="space-y-2 text-rose-300">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-rose-400">
                      <AlertTriangle className="w-4 h-4 text-rose-400" />
                      <span>❌ Compilation Failed</span>
                    </div>

                    {errorDiagnostic && (
                      <pre className="p-2 rounded bg-rose-950/30 border border-rose-500/30 text-rose-300 text-[11px] whitespace-pre-wrap overflow-x-auto">
                        {(errorDiagnostic as any).pointer || (errorDiagnostic as any).compiler_output || (errorDiagnostic as any).message}
                      </pre>
                    )}

                    {(errorDiagnostic as any)?.suggested_fix && (
                      <div className="p-2 rounded bg-emerald-950/30 border border-emerald-500/30 flex items-center justify-between gap-2 font-sans">
                        <div className="text-[11px]">
                          <span className="font-bold text-emerald-400">Quick Fix: </span>
                          <code className="text-emerald-300 font-mono">{(errorDiagnostic as any).suggested_fix}</code>
                        </div>
                        {onApplyFix && (
                          <button
                            onClick={() => onApplyFix((errorDiagnostic as any).suggested_fix)}
                            className="px-2.5 py-1 rounded bg-emerald-600 text-white font-bold text-xs shrink-0"
                          >
                            Apply Fix
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                ) : universalResult?.execution?.stdout ? (
                  <pre className="text-emerald-300 whitespace-pre-wrap leading-relaxed">
                    {universalResult.execution.stdout}
                  </pre>
                ) : (
                  <span className="text-gray-500 italic">No output yet. Tap "▶ Run" to execute code.</span>
                )}
              </div>

              {/* Mobile Complexity & Metrics Card */}
              {universalResult?.complexity && (
                <div className="p-3 rounded-xl bg-[#0F1528] border border-gray-800 space-y-2 font-sans">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-purple-400 block">Complexity & Runtime</span>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2.5 rounded-lg bg-black/40 border border-gray-800">
                      <span className="text-[10px] text-gray-400 block">Time Complexity</span>
                      <span className="text-lg font-extrabold text-white font-mono">{universalResult.complexity.time}</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-black/40 border border-gray-800">
                      <span className="text-[10px] text-gray-400 block">Space Complexity</span>
                      <span className="text-lg font-extrabold text-white font-mono">{universalResult.complexity.space}</span>
                    </div>
                    <div className="p-2 rounded-lg bg-black/40 border border-gray-800 text-[11px]">
                      <span className="text-gray-500 block text-[10px]">Runtime</span>
                      <span className="font-mono font-bold text-emerald-400">{universalResult.execution.runtime_ms} ms</span>
                    </div>
                    <div className="p-2 rounded-lg bg-black/40 border border-gray-800 text-[11px]">
                      <span className="text-gray-500 block text-[10px]">Peak Memory</span>
                      <span className="font-mono font-bold text-blue-400">{universalResult.execution.memory_mb} MB</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Files & Upload Tab */}
        {activeBottomNav === 'files' && (
          <div className="flex-1 p-4 space-y-4 font-sans text-xs">
            <div className="flex items-center justify-between border-b border-gray-800 pb-2">
              <span className="font-bold text-sm text-white">Project Files & Upload</span>
              <button
                onClick={onOpenFileUpload}
                className="px-3 py-1.5 rounded-lg bg-blue-600 text-white font-bold text-xs flex items-center gap-1"
              >
                <Upload className="w-3.5 h-3.5" />
                <span>Upload Code</span>
              </button>
            </div>

            <div className="p-4 rounded-xl bg-blue-600/10 border border-blue-500/30 text-blue-300 space-y-2 text-center">
              <Upload className="w-8 h-8 mx-auto text-blue-400" />
              <div className="font-bold text-sm">Upload from Phone Storage</div>
              <p className="text-gray-400 text-xs">Tap to pick `.py`, `.cpp`, `.java`, `.js`, or `.zip` files from your device.</p>
              <button
                onClick={onOpenFileUpload}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs"
              >
                Browse Device Files
              </button>
            </div>

            <div className="space-y-2 pt-2">
              <span className="text-[10px] uppercase font-bold text-gray-400 block">Available Cloud Projects</span>
              {cloudProjects.map((p) => (
                <div
                  key={p.id}
                  onClick={() => {
                    onLoadCloudProject(p.id);
                    setActiveBottomNav('code');
                  }}
                  className="p-3 rounded-xl bg-gray-900/80 border border-gray-800 active:bg-gray-800 space-y-1 cursor-pointer"
                >
                  <div className="flex items-center justify-between font-bold text-xs text-white">
                    <span>{p.title}</span>
                    <span className="text-[10px] uppercase text-blue-400 font-mono">{p.language}</span>
                  </div>
                  <p className="text-[11px] text-gray-400 line-clamp-1">{p.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Debug Tab */}
        {activeBottomNav === 'debug' && (
          <div className="flex-1 p-4 space-y-4 font-sans text-xs">
            <div className="border-b border-gray-800 pb-2">
              <span className="font-bold text-sm text-white flex items-center gap-1.5">
                <Bug className="w-4 h-4 text-indigo-400" /> Mobile Step Debugger
              </span>
            </div>
            <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 text-indigo-300 space-y-2">
              <p>Step through execution frames and monitor variable states.</p>
              <button
                onClick={() => {
                  onRun();
                  setActiveBottomNav('code');
                }}
                className="w-full py-2 rounded-xl bg-indigo-600 text-white font-bold text-xs"
              >
                Start Debug Session
              </button>
            </div>
          </div>
        )}

        {/* AI Tab */}
        {activeBottomNav === 'ai' && (
          <div className="flex-1 p-4 space-y-4 font-sans text-xs">
            <div className="border-b border-gray-800 pb-2">
              <span className="font-bold text-sm text-white flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-purple-400" /> CodePrism AI Assistant
              </span>
            </div>

            {/* Quick Action Chips */}
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => onAskAI('explain')}
                className="p-3 rounded-xl bg-gray-800/80 active:bg-blue-600 text-left border border-gray-700 text-xs font-semibold text-gray-200 flex items-center gap-2"
              >
                <Lightbulb className="w-4 h-4 text-amber-400" />
                <span>Explain Code</span>
              </button>
              <button
                onClick={() => onAskAI('optimize')}
                className="p-3 rounded-xl bg-gray-800/80 active:bg-purple-600 text-left border border-gray-700 text-xs font-semibold text-gray-200 flex items-center gap-2"
              >
                <Zap className="w-4 h-4 text-purple-400" />
                <span>Optimize Big-O</span>
              </button>
              <button
                onClick={() => onAskAI('tests')}
                className="p-3 rounded-xl bg-gray-800/80 active:bg-emerald-600 text-left border border-gray-700 text-xs font-semibold text-gray-200 flex items-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Generate Tests</span>
              </button>
              <button
                onClick={() => onAskAI('security')}
                className="p-3 rounded-xl bg-gray-800/80 active:bg-rose-600 text-left border border-gray-700 text-xs font-semibold text-gray-200 flex items-center gap-2"
              >
                <ShieldCheck className="w-4 h-4 text-rose-400" />
                <span>Fix Security</span>
              </button>
            </div>

            {aiResponse && (
              <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 space-y-2 text-xs">
                <div className="font-bold text-purple-200 text-sm">{aiResponse.title}</div>
                <p className="text-gray-300 leading-relaxed">{aiResponse.content}</p>
                {aiResponse.bullet_points && (
                  <ul className="list-disc list-inside space-y-1 text-gray-300 text-[11px] pt-1">
                    {aiResponse.bullet_points.map((pt, idx) => (
                      <li key={idx}>{pt}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        )}

        {/* Cloud & PWA Install Tab */}
        {activeBottomNav === 'cloud' && (
          <div className="flex-1 p-4 space-y-4 font-sans text-xs">
            <div className="border-b border-gray-800 pb-2">
              <span className="font-bold text-sm text-white flex items-center gap-1.5">
                <Folder className="w-4 h-4 text-blue-400" /> Cloud Projects & Install
              </span>
            </div>

            {/* Install PWA Button */}
            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-emerald-300 space-y-2">
              <div className="font-bold text-sm">Install CodePrism PWA</div>
              <p className="text-xs text-gray-400">Run CodePrism as a full-screen app on your phone home screen.</p>
              <PWAInstallButton isMobileDrawer={true} mode="mobile" />
            </div>

            {/* Save Current Project */}
            <button
              onClick={onSaveCloudProject}
              className="w-full py-2.5 rounded-xl bg-blue-600 text-white font-bold text-xs shadow-md"
            >
              Save Current Code to Cloud
            </button>
          </div>
        )}
      </main>

      {/* Mobile Bottom Tab Navigation */}
      <nav className="h-14 bg-[#0A0E1A] border-t border-gray-800 px-1 flex items-center justify-around shrink-0 text-[10px] font-semibold text-gray-400">
        <button
          onClick={() => setActiveBottomNav('code')}
          className={`flex flex-col items-center gap-1 py-1 px-3 transition-colors ${
            activeBottomNav === 'code' ? 'text-emerald-400 font-bold' : 'hover:text-gray-200'
          }`}
        >
          <Code2 className="w-4 h-4" />
          <span>Code</span>
        </button>

        <button
          onClick={() => setActiveBottomNav('files')}
          className={`flex flex-col items-center gap-1 py-1 px-3 transition-colors ${
            activeBottomNav === 'files' ? 'text-blue-400 font-bold' : 'hover:text-gray-200'
          }`}
        >
          <Folder className="w-4 h-4" />
          <span>Files</span>
        </button>

        <button
          onClick={() => setActiveBottomNav('debug')}
          className={`flex flex-col items-center gap-1 py-1 px-3 transition-colors ${
            activeBottomNav === 'debug' ? 'text-indigo-400 font-bold' : 'hover:text-gray-200'
          }`}
        >
          <Bug className="w-4 h-4" />
          <span>Debug</span>
        </button>

        <button
          onClick={() => setActiveBottomNav('ai')}
          className={`flex flex-col items-center gap-1 py-1 px-3 transition-colors ${
            activeBottomNav === 'ai' ? 'text-purple-400 font-bold' : 'hover:text-gray-200'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>AI</span>
        </button>

        <button
          onClick={() => setActiveBottomNav('cloud')}
          className={`flex flex-col items-center gap-1 py-1 px-3 transition-colors ${
            activeBottomNav === 'cloud' ? 'text-emerald-400 font-bold' : 'hover:text-gray-200'
          }`}
        >
          <Download className="w-4 h-4" />
          <span>App & Cloud</span>
        </button>
      </nav>
    </div>
  );
};
