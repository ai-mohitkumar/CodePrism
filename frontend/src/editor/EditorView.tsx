import React, { useRef, useEffect, useState } from 'react';
import Editor, { OnMount, Monaco } from '@monaco-editor/react';
import { 
  FileCode, 
  Save, 
  Download, 
  Check, 
  Edit2, 
  HardDrive, 
  Cpu, 
  ChevronDown 
} from 'lucide-react';

interface EditorViewProps {
  filename: string;
  language: string;
  code: string;
  onChange: (value: string) => void;
  onRun: () => void;
  onRenameFile?: (newFilename: string) => void;
  onSaveToSession?: (filename: string, code: string) => void;
  onDownloadToDevice?: (filename: string, code: string) => void;
  isUnsaved?: boolean;
  breakpoints: number[];
  onToggleBreakpoint: (line: number) => void;
  currentDebugLine?: number | null;
  errorLine?: number | null;
}

export const EditorView: React.FC<EditorViewProps> = ({
  filename,
  language,
  code,
  onChange,
  onRun,
  onRenameFile,
  onSaveToSession,
  onDownloadToDevice,
  isUnsaved = false,
  breakpoints,
  onToggleBreakpoint,
  currentDebugLine,
  errorLine,
}) => {
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<Monaco | null>(null);
  const decorationsRef = useRef<string[]>([]);

  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState(filename);
  const [showSaveMenu, setShowSaveMenu] = useState(false);
  const [saveFlash, setSaveFlash] = useState<string | null>(null);

  useEffect(() => {
    setEditedName(filename);
  }, [filename]);

  const monacoLang = 
    language === 'cpp' ? 'cpp' : 
    language === 'java' ? 'java' :
    language === 'javascript' ? 'javascript' : 
    language === 'typescript' ? 'typescript' :
    language === 'csharp' ? 'csharp' :
    language === 'rust' ? 'rust' :
    language === 'go' ? 'go' :
    language === 'sql' ? 'sql' : 'python';

  const handleSaveRAM = () => {
    if (onSaveToSession) {
      onSaveToSession(filename, code);
      setSaveFlash('Saved to Session (RAM) ✓');
      setTimeout(() => setSaveFlash(null), 2000);
      setShowSaveMenu(false);
    }
  };

  const handleDownloadFile = () => {
    if (onDownloadToDevice) {
      onDownloadToDevice(filename, code);
    } else {
      const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      a.click();
      URL.revokeObjectURL(a.href);
    }
    setSaveFlash('Downloaded to Device 📥');
    setTimeout(() => setSaveFlash(null), 2000);
    setShowSaveMenu(false);
  };

  const handleFinishRename = () => {
    if (editedName.trim() && editedName !== filename && onRenameFile) {
      onRenameFile(editedName.trim());
    }
    setIsEditingName(false);
  };

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Ctrl+Enter or F5 to Run
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      onRun();
    });
    editor.addCommand(monaco.KeyCode.F5, () => {
      onRun();
    });

    // Ctrl+S or Cmd+S to Save to Session
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      handleSaveRAM();
    });

    // Margin glyph click for breakpoints
    editor.onMouseDown((e: any) => {
      if (e.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        const line = e.target.position?.lineNumber;
        if (line) {
          onToggleBreakpoint(line);
        }
      }
    });
  };

  // Keyboard event listener for global Ctrl+S
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSaveRAM();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [filename, code]);

  // Update decorations for breakpoints, current execution line, and errors
  useEffect(() => {
    if (editorRef.current && monacoRef.current) {
      const monaco = monacoRef.current;
      const newDecorations: any[] = [];

      // Breakpoints
      breakpoints.forEach((line) => {
        newDecorations.push({
          range: new monaco.Range(line, 1, line, 1),
          options: {
            isWholeLine: false,
            glyphMarginClassName: 'bg-rose-500 rounded-full w-3 h-3 m-1 cursor-pointer shadow-lg shadow-rose-500/50',
            glyphMarginHoverMessage: { value: `Breakpoint on line ${line}` },
          },
        });
      });

      // Current debug execution line
      if (currentDebugLine && currentDebugLine > 0) {
        newDecorations.push({
          range: new monaco.Range(currentDebugLine, 1, currentDebugLine, 1),
          options: {
            isWholeLine: true,
            className: 'bg-yellow-500/20 border-l-4 border-yellow-400',
            glyphMarginClassName: 'bg-yellow-400 w-3 h-3 rounded m-1',
          },
        });
      }

      // Syntax / Runtime error line
      if (errorLine && errorLine > 0) {
        newDecorations.push({
          range: new monaco.Range(errorLine, 1, errorLine, 1),
          options: {
            isWholeLine: true,
            className: 'bg-rose-950/40 border-l-4 border-rose-500',
            overviewRuler: {
              color: '#f43f5e',
              position: monaco.editor.OverviewRulerLane.Full,
            },
          },
        });
      }

      decorationsRef.current = editorRef.current.deltaDecorations(decorationsRef.current, newDecorations);
    }
  }, [breakpoints, currentDebugLine, errorLine]);

  return (
    <div className="flex flex-col h-full bg-[#0E1322] border-r border-gray-800">
      {/* Interactive Editor Tab & Save Bar */}
      <div className="h-9 px-2 border-b border-gray-800/80 bg-[#12182B] flex items-center justify-between text-xs select-none relative">
        <div className="flex items-center gap-1.5">
          {/* Active File Tab with Unsaved indicator ● */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-t-md bg-[#0E1322] border-t-2 border-blue-500 text-gray-200 font-mono text-xs shadow-sm">
            <FileCode className="w-3.5 h-3.5 text-blue-400" />
            
            {isEditingName ? (
              <input
                type="text"
                autoFocus
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                onBlur={handleFinishRename}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleFinishRename();
                  if (e.key === 'Escape') { setEditedName(filename); setIsEditingName(false); }
                }}
                className="bg-gray-900 text-white px-1 py-0.5 rounded border border-blue-500 text-xs font-mono focus:outline-none w-28"
              />
            ) : (
              <span 
                onDoubleClick={() => setIsEditingName(true)}
                title="Double click to rename"
                className="cursor-pointer hover:text-white"
              >
                {filename}
              </span>
            )}

            {/* Unsaved indicator dot ● */}
            {isUnsaved && (
              <span className="w-2 h-2 rounded-full bg-blue-400" title="Unsaved changes"></span>
            )}

            {errorLine && (
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" title={`Error on line ${errorLine}`}></span>
            )}
          </div>

          {/* Toast Notification */}
          {saveFlash && (
            <span className="text-[11px] text-emerald-400 font-semibold px-2 py-0.5 bg-emerald-500/10 rounded border border-emerald-500/20 animate-fade-in font-mono">
              {saveFlash}
            </span>
          )}
        </div>

        {/* Right Controls: Save Button Dropdown + Info */}
        <div className="flex items-center gap-2 pr-1">
          {/* Dual Save Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowSaveMenu(!showSaveMenu)}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-200 text-xs font-semibold shadow-sm transition-all"
              title="Save options (RAM / Device Download)"
            >
              <Save className="w-3.5 h-3.5 text-blue-400" />
              <span>Save</span>
              <ChevronDown className="w-3 h-3 text-gray-400" />
            </button>

            {showSaveMenu && (
              <div className="absolute right-0 top-8 w-56 bg-[#0E1424] border border-gray-700 rounded-xl shadow-2xl p-1.5 z-30 font-sans text-xs space-y-1">
                <button
                  onClick={handleSaveRAM}
                  className="w-full flex items-center gap-2 px-2.5 py-2 rounded-lg hover:bg-gray-800 text-left text-gray-200 transition-colors"
                >
                  <Cpu className="w-4 h-4 text-emerald-400 shrink-0" />
                  <div>
                    <span className="font-bold block">Save to Session (RAM)</span>
                    <span className="text-[10px] text-gray-400 block font-mono">Ctrl+S • In-Memory Buffer</span>
                  </div>
                </button>

                <button
                  onClick={handleDownloadFile}
                  className="w-full flex items-center gap-2 px-2.5 py-2 rounded-lg hover:bg-gray-800 text-left text-gray-200 transition-colors"
                >
                  <Download className="w-4 h-4 text-blue-400 shrink-0" />
                  <div>
                    <span className="font-bold block">Download to Device</span>
                    <span className="text-[10px] text-gray-400 block font-mono">Save {filename} to Downloads</span>
                  </div>
                </button>
              </div>
            )}
          </div>

          <div className="hidden sm:flex items-center gap-3 text-[11px] font-mono text-gray-400 pl-2">
            <span>{monacoLang.toUpperCase()}</span>
            <span>{code.split('\n').length} lines</span>
          </div>
        </div>
      </div>

      {/* Monaco Editor Canvas */}
      <div className="flex-1 relative min-h-0">
        <Editor
          height="100%"
          language={monacoLang}
          value={code}
          theme="vs-dark"
          onChange={(val) => onChange(val || '')}
          onMount={handleEditorDidMount}
          options={{
            fontSize: 14,
            fontFamily: '"Fira Code", "JetBrains Mono", Consolas, monospace',
            fontLigatures: true,
            minimap: { enabled: false },
            glyphMargin: true,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            renderLineHighlight: 'all',
            padding: { top: 10, bottom: 10 },
            cursorBlinking: 'smooth',
            smoothScrolling: true,
            tabSize: 4,
          }}
        />
      </div>
    </div>
  );
};
