import React, { useState, useEffect, useRef, useCallback } from 'react';
import { TopBar } from './components/TopBar';
import { Sidebar, ActiveSidebarTab } from './components/Sidebar';
import { FileTree } from './components/FileTree';
import { EditorView } from './editor/EditorView';
import { TerminalPanel } from './terminal/TerminalPanel';
import { CompilerPanel } from './components/CompilerPanel';
import { DebuggerPanel } from './debugger/DebuggerPanel';
import { AnalyzerPanel } from './analyzer/AnalyzerPanel';
import { AIAssistantPanel } from './ai/AIAssistantPanel';
import { UploadModal } from './components/UploadModal';
import { ProjectReportModal } from './components/ProjectReportModal';
import { AnalysisModal } from './components/AnalysisModal';
import { ProjectHistoryModal } from './components/ProjectHistoryModal';
import { MobileView } from './mobile/MobileView';
import { apiService } from './services/api';
import { 
  UniversalResult, ErrorDiagnosis, ASTResponse, 
  DebugStepResponse, AIResponse, LanguageMeta, CompileResponse,
  FileUploadResponse, ProjectReportResponse, ProjectFileSummary,
  ProjectMetadata, ProjectDetails, ProjectTemplate 
} from './types';

const INITIAL_PROJECT_FILES = [
  { name: 'main.py', language: 'python' },
  { name: 'solution.cpp', language: 'cpp' },
  { name: 'Main.java', language: 'java' },
  { name: 'app.js', language: 'javascript' },
  { name: 'server.ts', language: 'typescript' },
  { name: 'Program.cs', language: 'csharp' },
  { name: 'main.rs', language: 'rust' },
  { name: 'main.go', language: 'go' },
  { name: 'query.sql', language: 'sql' },
];

export interface LocalSessionFile {
  name: string;
  code: string;
  savedAt: number;
}

export const App: React.FC = () => {
  const [currentProjectId, setCurrentProjectId] = useState<string>('proj_bubble_sort');
  const [projectTitle, setProjectTitle] = useState<string>('Bubble Sort & Complexity Analysis');
  const [projectFiles, setProjectFiles] = useState(INITIAL_PROJECT_FILES);
  const [activeFile, setActiveFile] = useState<string>('main.py');
  const [language, setLanguage] = useState<string>('python');
  const [codeMap, setCodeMap] = useState<Record<string, string>>({
    'main.py': `for i in range(10):
    print(i)
`,
    'solution.cpp': `#include <iostream>
#include <vector>

int findMax(const std::vector<int>& arr) {
    int maxVal = arr[0];
    for (int x : arr) {
        if (x > maxVal) maxVal = x;
    }
    return maxVal;
}

int main() {
    std::vector<int> numbers = {10, 20, 5, 30};
    std::cout << "Maximum element: " << findMax(numbers) << std::endl;
    return 0;
}
`,
    'Main.java': `public class Main {
    public static int findMax(int[] arr) {
        int max = arr[0];
        for (int x : arr) {
            if (x > max) max = x;
        }
        return max;
    }

    public static void main(String[] args) {
        int[] numbers = {10, 20, 5, 30};
        System.out.println("Maximum element: " + findMax(numbers));
    }
}
`,
    'app.js': `function findMax(arr) {
    let maximum = arr[0];
    for (let i = 0; i < arr.length; i++) {
        if (arr[i] > maximum) maximum = arr[i];
    }
    return maximum;
}

const numbers = [10, 20, 5, 30];
console.log("Maximum element:", findMax(numbers));
`,
    'server.ts': `function findMax(arr: number[]): number {
    let maximum = arr[0];
    for (const x of arr) {
        if (x > maximum) maximum = x;
    }
    return maximum;
}

const numbers: number[] = [10, 20, 5, 30];
console.log("Maximum element:", findMax(numbers));
`,
    'Program.cs': `using System;

class Program {
    static int FindMax(int[] arr) {
        int max = arr[0];
        foreach (int x in arr) {
            if (x > max) max = x;
        }
        return max;
    }

    static void Main() {
        int[] numbers = {10, 20, 5, 30};
        Console.WriteLine($"Maximum element: {FindMax(numbers)}");
    }
}
`,
    'main.rs': `fn find_max(arr: &[i32]) -> i32 {
    let mut max = arr[0];
    for &x in arr {
        if x > max { max = x; }
    }
    max
}

fn main() {
    let numbers = [10, 20, 5, 30];
    println!("Maximum element: {}", find_max(&numbers));
}
`,
    'main.go': `package main

import "fmt"

func findMax(arr []int) int {
    max := arr[0]
    for _, x := range arr {
        if x > max {
            max = x
        }
    }
    return max
}

func main() {
    numbers := []int{10, 20, 5, 30}
    fmt.Printf("Maximum element: %d\\n", findMax(numbers))
}
`,
    'query.sql': `CREATE TABLE employees (id INT PRIMARY KEY, name TEXT, salary INT);
INSERT INTO employees VALUES (1, 'Alice', 95000), (2, 'Bob', 120000), (3, 'Charlie', 88000);

SELECT name, salary FROM employees WHERE salary > 90000 ORDER BY salary DESC;
`
  });

  // Local Session (RAM & LocalStorage) Files
  const [sessionFiles, setSessionFiles] = useState<LocalSessionFile[]>(() => {
    try {
      const saved = localStorage.getItem('codeprism_session_files');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [savedBaselineCode, setSavedBaselineCode] = useState<string>('');

  const [stdin, setStdin] = useState<string>('');
  const [activeSidebar, setActiveSidebar] = useState<ActiveSidebarTab>('files');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  const [languagesList, setLanguagesList] = useState<LanguageMeta[]>([]);
  const [templates, setTemplates] = useState<Record<string, Record<string, string>>>({});
  const [cloudProjects, setCloudProjects] = useState<ProjectMetadata[]>([]);
  const [autosaveStatus, setAutosaveStatus] = useState<'synced' | 'saving' | 'unsaved'>('synced');

  // Mobile view toggle (responsive auto-detect + manual toggle)
  const [isMobileMode, setIsMobileMode] = useState<boolean>(() => {
    return typeof window !== 'undefined' ? window.innerWidth < 768 : false;
  });

  // Modals state
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [isProjectReportOpen, setIsProjectReportOpen] = useState<boolean>(false);
  const [isAnalysisOpen, setIsAnalysisOpen] = useState<boolean>(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
  const [projectReport, setProjectReport] = useState<ProjectReportResponse | null>(null);

  // Compiler State
  const [compileData, setCompileData] = useState<CompileResponse | null>(null);

  // Universal Result State
  const [universalResult, setUniversalResult] = useState<UniversalResult | null>(null);
  const [diagnosis, setDiagnosis] = useState<ErrorDiagnosis | null>(null);

  // Debugger state
  const [breakpoints, setBreakpoints] = useState<number[]>([4]);
  const [debugState, setDebugState] = useState<DebugStepResponse | null>(null);
  const [isDebugging, setIsDebugging] = useState<boolean>(false);

  // AI Assistant state
  const [aiResponse, setAiResponse] = useState<AIResponse | null>(null);
  const [aiLoading, setAiLoading] = useState<boolean>(false);

  const currentCode = codeMap[activeFile] || '';
  const isUnsaved = savedBaselineCode !== '' && currentCode !== savedBaselineCode;
  const autosaveTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Initial load
  useEffect(() => {
    const init = async () => {
      try {
        const [res, projectsRes] = await Promise.all([
          apiService.getLanguages(),
          apiService.listProjects().catch(() => [])
        ]);
        if (res.languages) setLanguagesList(res.languages);
        if (res.templates) setTemplates(res.templates);
        if (projectsRes) setCloudProjects(projectsRes);
        setIsBackendConnected(true);
      } catch {
        setIsBackendConnected(false);
      }
    };
    init();
    setSavedBaselineCode(codeMap['main.py'] || '');
  }, []);

  // Sync session files to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('codeprism_session_files', JSON.stringify(sessionFiles));
    } catch (e) {
      console.error(e);
    }
  }, [sessionFiles]);

  // Real-Time Debounced Autosave to Cloud
  useEffect(() => {
    setAutosaveStatus('unsaved');
    if (autosaveTimerRef.current) {
      clearTimeout(autosaveTimerRef.current);
    }

    autosaveTimerRef.current = setTimeout(async () => {
      setAutosaveStatus('saving');
      try {
        await apiService.saveProject({
          project_id: currentProjectId,
          title: projectTitle,
          language,
          files: Object.entries(codeMap).map(([name, content]) => ({
            name,
            language: name.endsWith('.cpp') ? 'cpp' : name.endsWith('.java') ? 'java' : name.endsWith('.js') ? 'javascript' : name.endsWith('.ts') ? 'typescript' : name.endsWith('.cs') ? 'csharp' : name.endsWith('.rs') ? 'rust' : name.endsWith('.go') ? 'go' : name.endsWith('.sql') ? 'sql' : 'python',
            content
          })),
          is_autosave: true
        });
        setAutosaveStatus('synced');
        setSavedBaselineCode(currentCode);
      } catch (e) {
        setAutosaveStatus('unsaved');
      }
    }, 2500);

    return () => {
      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
      }
    };
  }, [codeMap, currentProjectId, projectTitle, language]);

  const detectLanguageFromFilename = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase() || 'py';
    const langMap: Record<string, string> = {
      py: 'python',
      cpp: 'cpp',
      c: 'c',
      cc: 'cpp',
      java: 'java',
      js: 'javascript',
      jsx: 'javascript',
      ts: 'typescript',
      tsx: 'typescript',
      cs: 'csharp',
      rs: 'rust',
      go: 'go',
      sql: 'sql'
    };
    return langMap[ext] || 'python';
  };

  const handleSelectFile = (file: { name: string; language: string }) => {
    setActiveFile(file.name);
    setLanguage(file.language);
    setSavedBaselineCode(codeMap[file.name] || '');
  };

  const handleCodeChange = (newCode: string) => {
    setCodeMap((prev) => ({ ...prev, [activeFile]: newCode }));
  };

  // Save to Session (RAM & localStorage)
  const handleSaveToSession = (filename: string, code: string) => {
    setSessionFiles((prev) => {
      const filtered = prev.filter((f) => f.name !== filename);
      return [{ name: filename, code, savedAt: Date.now() }, ...filtered];
    });
    setSavedBaselineCode(code);
  };

  // Download directly to Device
  const handleDownloadToDevice = (filename: string, code: string) => {
    const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
    setSavedBaselineCode(code);
  };

  // Select a file from local session
  const handleSelectSessionFile = (sf: LocalSessionFile) => {
    const detectedLang = detectLanguageFromFilename(sf.name);
    setCodeMap((prev) => ({ ...prev, [sf.name]: sf.code }));
    setProjectFiles((prev) => {
      if (!prev.some((f) => f.name === sf.name)) {
        return [{ name: sf.name, language: detectedLang }, ...prev];
      }
      return prev;
    });
    setActiveFile(sf.name);
    setLanguage(detectedLang);
    setSavedBaselineCode(sf.code);
  };

  // Delete from local session
  const handleDeleteSessionFile = (filename: string) => {
    setSessionFiles((prev) => prev.filter((f) => f.name !== filename));
  };

  // Rename File with auto language detection
  const handleRenameFile = (newFilename: string) => {
    if (!newFilename.trim()) return;
    const oldName = activeFile;
    if (newFilename === oldName) return;

    const detectedLang = detectLanguageFromFilename(newFilename);
    const content = codeMap[oldName] || '';

    setCodeMap((prev) => {
      const copy = { ...prev };
      delete copy[oldName];
      copy[newFilename] = content;
      return copy;
    });

    setProjectFiles((prev) => 
      prev.map((f) => f.name === oldName ? { name: newFilename, language: detectedLang } : f)
    );

    setActiveFile(newFilename);
    setLanguage(detectedLang);
  };

  const handleAddNewFile = (filename: string) => {
    if (codeMap[filename] !== undefined) {
      alert(`File "${filename}" already exists in project.`);
      return;
    }
    const detectedLang = detectLanguageFromFilename(filename);
    const newFileItem = { name: filename, language: detectedLang };
    setProjectFiles((prev) => [...prev, newFileItem]);
    setCodeMap((prev) => ({ ...prev, [filename]: `# ${filename}\n` }));
    setActiveFile(filename);
    setLanguage(detectedLang);
    setSavedBaselineCode(`# ${filename}\n`);
  };

  const handleDeleteFile = (filename: string) => {
    setProjectFiles((prev) => prev.filter((f) => f.name !== filename));
    setCodeMap((prev) => {
      const copy = { ...prev };
      delete copy[filename];
      return copy;
    });
    const remaining = projectFiles.filter((f) => f.name !== filename);
    if (remaining.length > 0) {
      setActiveFile(remaining[0].name);
      setLanguage(remaining[0].language);
      setSavedBaselineCode(codeMap[remaining[0].name] || '');
    }
  };

  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang);
    const meta = languagesList.find((l) => l.id === newLang);
    const ext = meta?.extension || newLang;
    const newName = `solution.${ext}`;
    if (!codeMap[newName]) {
      const templ = templates[newLang]?.find_max || `// ${newLang} code template`;
      setCodeMap((prev) => ({ ...prev, [newName]: templ }));
      setProjectFiles((prev) => {
        if (!prev.some((f) => f.name === newName)) {
          return [{ name: newName, language: newLang }, ...prev];
        }
        return prev;
      });
    }
    setActiveFile(newName);
  };

  const handleLoadPreset = (presetKey: string) => {
    const code = templates[language]?.[presetKey];
    if (code) {
      handleCodeChange(code);
    }
  };

  const handleCompile = async (flags: string[] = ['-O2']) => {
    setIsLoading(true);
    setUniversalResult(null);
    setDiagnosis(null);
    try {
      const cRes = await apiService.compileCode(language, currentCode, flags);
      setCompileData(cRes);
      const diag = await apiService.analyzeErrors(language, currentCode);
      setDiagnosis(diag);
      setActiveSidebar('compiler');
      setIsBackendConnected(true);
    } catch (err: any) {
      setCompileData({
        success: false,
        compiler_name: language,
        artifact_type: 'Unknown',
        compilation_time_ms: 0,
        errors_count: 1,
        warnings_count: 0,
        raw_output: err.message || 'Compilation error.',
        diagnostics: []
      });
      setIsBackendConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRun = async () => {
    setIsLoading(true);
    setUniversalResult(null);
    setDiagnosis(null);
    try {
      const [res, diag] = await Promise.all([
        apiService.executeCode(language, currentCode, stdin),
        apiService.analyzeErrors(language, currentCode)
      ]);
      setUniversalResult(res);
      setDiagnosis(diag);
      setIsBackendConnected(true);
    } catch (err: any) {
      setUniversalResult({
        language,
        version: 'Unknown',
        status: 'runtime_error',
        filename: activeFile,
        compile: { success: false, compiler_output: err.message || 'Execution error.', errors: [err.message || 'Error'], warnings: [] },
        execution: {
          exit_code: 1,
          stdout: '',
          stderr: err.message || 'Execution error.',
          runtime_ms: 0,
          memory_mb: 0,
          cpu_percent: 0,
          functions: [],
          status: 'runtime_error',
        },
        ast: null,
        complexity: { time: 'Unknown', space: 'Unknown', confidence: 0, reason: '', nested_depth: 0, has_recursion: false, has_halving: false, details: [] },
        quality: { score: 50, maintainability: 5, readability: 5, cyclomatic: 1, total_lines: 0, code_lines: 0, comment_lines: 0, issues: [] },
        security: { critical: 0, high: 0, medium: 0, low: 0, issues: [] }
      });
      setIsBackendConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setIsLoading(true);
    try {
      const full = await apiService.analyzeFull(language, currentCode, stdin);
      setUniversalResult(full);
      setIsAnalysisOpen(true);
      setIsBackendConnected(true);
    } catch {
      setIsBackendConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveCloudProject = async () => {
    try {
      setAutosaveStatus('saving');
      const saved = await apiService.saveProject({
        project_id: currentProjectId,
        title: projectTitle,
        language,
        files: Object.entries(codeMap).map(([name, content]) => ({
          name,
          language,
          content
        })),
        is_autosave: false
      });
      const updated = await apiService.listProjects();
      setCloudProjects(updated);
      setAutosaveStatus('synced');
      setSavedBaselineCode(currentCode);
      alert(`✓ Project "${saved.title}" saved & snapshot captured!`);
    } catch (e: any) {
      setAutosaveStatus('unsaved');
      alert("Failed to save project to cloud: " + e.message);
    }
  };

  const handleLoadCloudProject = async (projectId: string) => {
    try {
      const proj = await apiService.getProject(projectId);
      if (proj && proj.files && proj.files.length > 0) {
        setCurrentProjectId(proj.id);
        setProjectTitle(proj.title);
        const newMap: Record<string, string> = {};
        proj.files.forEach(f => {
          newMap[f.name] = f.content;
        });
        setCodeMap(newMap);
        setProjectFiles(proj.files.map(f => ({ name: f.name, language: f.language })));
        setActiveFile(proj.files[0].name);
        setLanguage(proj.files[0].language);
        setSavedBaselineCode(proj.files[0].content);
        setAutosaveStatus('synced');
        alert(`✓ Loaded project "${proj.title}"!`);
      }
    } catch (e: any) {
      alert("Failed to load project: " + e.message);
    }
  };

  const handleRestoreProject = (restored: ProjectDetails) => {
    setCurrentProjectId(restored.id);
    setProjectTitle(restored.title);
    const newMap: Record<string, string> = {};
    restored.files.forEach((f) => {
      newMap[f.name] = f.content;
    });
    setCodeMap(newMap);
    setProjectFiles(restored.files.map((f) => ({ name: f.name, language: f.language })));
    setActiveFile(restored.files[0].name);
    setLanguage(restored.files[0].language);
    setSavedBaselineCode(restored.files[0].content);
    setAutosaveStatus('synced');
    alert(`✓ Project restored to previous snapshot version!`);
  };

  const handleLoadTemplate = (tmpl: ProjectTemplate) => {
    const newId = `proj_${tmpl.id}_${Date.now()}`;
    setCurrentProjectId(newId);
    setProjectTitle(tmpl.title);
    setLanguage(tmpl.language);
    const newMap: Record<string, string> = {};
    tmpl.files.forEach((f) => {
      newMap[f.name] = f.content;
    });
    setCodeMap(newMap);
    setProjectFiles(tmpl.files.map((f) => ({ name: f.name, language: f.language })));
    setActiveFile(tmpl.files[0].name);
    setSavedBaselineCode(tmpl.files[0].content);
    setAutosaveStatus('synced');
    alert(`✓ Initialized project with template "${tmpl.title}"!`);
  };

  const handleSingleFileUploaded = (res: FileUploadResponse) => {
    const filename = res.filename;
    setActiveFile(filename);
    setLanguage(res.language);
    setCodeMap((prev) => ({ ...prev, [filename]: res.code }));

    setProjectFiles((prev) => {
      if (!prev.some((f) => f.name === filename)) {
        return [{ name: filename, language: res.language }, ...prev];
      }
      return prev;
    });

    setUniversalResult(res.result);
    setSavedBaselineCode(res.code);
    setIsAnalysisOpen(true);
  };

  const handleProjectUploaded = (res: ProjectReportResponse) => {
    setProjectReport(res);
    setIsProjectReportOpen(true);

    if (res.files && res.files.length > 0) {
      const newFiles = res.files.map((f) => ({
        name: f.filename,
        language: f.language,
      }));
      setProjectFiles(newFiles);

      const newMap: Record<string, string> = {};
      res.files.forEach((f) => {
        newMap[f.filename] = f.code_snippet;
      });
      setCodeMap(newMap);

      setActiveFile(res.files[0].filename);
      setLanguage(res.files[0].language);
      setSavedBaselineCode(res.files[0].code_snippet);
    }
  };

  const handleOpenFileFromReport = (file: ProjectFileSummary) => {
    setActiveFile(file.filename);
    setLanguage(file.language);
    setCodeMap((prev) => ({ ...prev, [file.filename]: file.code_snippet }));
    setSavedBaselineCode(file.code_snippet);
  };

  const handleDebug = async () => {
    setIsDebugging(true);
    setActiveSidebar('debug');
    try {
      const res = await apiService.debugStep(language, currentCode, 1, breakpoints, {});
      setDebugState(res);
    } catch (e) {
      console.error(e);
    }
  };

  const handleStepOver = async () => {
    if (!debugState) return;
    try {
      const nextLine = debugState.current_line;
      const res = await apiService.debugStep(
        language, 
        currentCode, 
        nextLine, 
        breakpoints, 
        debugState.variables
      );
      setDebugState(res);
    } catch (e) {
      console.error(e);
    }
  };

  const handleToggleBreakpoint = (line: number) => {
    setBreakpoints((prev) => 
      prev.includes(line) ? prev.filter((l) => l !== line) : [...prev, line]
    );
  };

  const handleAskAI = async (promptType: string, query?: string) => {
    setAiLoading(true);
    setActiveSidebar('ai');
    try {
      const res = await apiService.aiAssistant(language, currentCode, promptType, query);
      setAiResponse(res);
    } catch {
      setAiResponse({
        title: 'AI Request Failed',
        content: 'Could not connect to AI assistant engine.',
        bullet_points: []
      });
    } finally {
      setAiLoading(false);
    }
  };

  const handleApplyFix = (fix: string) => {
    const errLine = compileData?.diagnostics?.[0]?.line || universalResult?.compile?.error_line || diagnosis?.line;
    if (errLine && errLine > 0) {
      const lines = currentCode.split('\n');
      lines[errLine - 1] = fix;
      const updated = lines.join('\n');
      handleCodeChange(updated);
      setDiagnosis(null);
      if (universalResult && universalResult.compile) {
        setUniversalResult({
          ...universalResult,
          compile: { ...universalResult.compile, success: true, errors: [], error_pointer: null }
        });
      }
    }
  };

  // Mobile View simulator
  if (isMobileMode) {
    return (
      <MobileView
        language={language}
        languages={languagesList}
        code={currentCode}
        onCodeChange={handleCodeChange}
        onLanguageChange={handleLanguageChange}
        onCompile={() => handleCompile(['-O2'])}
        onRun={handleRun}
        onAnalyze={handleAnalyze}
        onAskAI={(type) => handleAskAI(type)}
        onToggleDesktopView={() => setIsMobileMode(false)}
        onOpenFileUpload={() => setIsUploadOpen(true)}
        compileData={compileData}
        universalResult={universalResult}
        aiResponse={aiResponse}
        cloudProjects={cloudProjects}
        onLoadCloudProject={handleLoadCloudProject}
        onSaveCloudProject={handleSaveCloudProject}
        isLoading={isLoading}
      />
    );
  }

  // Desktop / PC IDE Layout
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0B0F19]">
      {/* TopBar Header */}
      <TopBar
        language={language}
        languages={languagesList}
        onLanguageChange={handleLanguageChange}
        onLoadPreset={handleLoadPreset}
        onCompile={() => handleCompile(['-O2'])}
        onRun={handleRun}
        onDebug={handleDebug}
        onAnalyze={handleAnalyze}
        onOpenUpload={() => setIsUploadOpen(true)}
        onToggleMobileView={() => setIsMobileMode(true)}
        onSaveCloudProject={handleSaveCloudProject}
        onOpenHistory={() => setIsHistoryOpen(true)}
        autosaveStatus={autosaveStatus}
        isLoading={isLoading}
        isBackendConnected={isBackendConnected}
      />

      {/* Main IDE Layout */}
      <div className="flex-1 flex min-h-0">
        {/* Activity Sidebar */}
        <Sidebar 
          activeTab={activeSidebar} 
          onSelectTab={setActiveSidebar} 
        />

        {/* Explorer Pane with Multi-File & Session Saves */}
        {activeSidebar === 'files' && (
          <FileTree
            files={projectFiles}
            activeFile={activeFile}
            onSelectFile={handleSelectFile}
            onAddNewFile={handleAddNewFile}
            onDeleteFile={handleDeleteFile}
            sessionFiles={sessionFiles}
            onSelectSessionFile={handleSelectSessionFile}
            onDeleteSessionFile={handleDeleteSessionFile}
            onDownloadFile={handleDownloadToDevice}
          />
        )}

        {/* Center: Editor + Bottom Terminal */}
        <div className="flex-1 flex flex-col min-h-0 min-w-0">
          <div className="flex-1 min-h-0">
            <EditorView
              filename={activeFile}
              language={language}
              code={currentCode}
              onChange={handleCodeChange}
              onRun={handleRun}
              onRenameFile={handleRenameFile}
              onSaveToSession={handleSaveToSession}
              onDownloadToDevice={handleDownloadToDevice}
              isUnsaved={isUnsaved}
              breakpoints={breakpoints}
              onToggleBreakpoint={handleToggleBreakpoint}
              currentDebugLine={isDebugging ? debugState?.current_line : null}
              errorLine={compileData?.diagnostics?.[0]?.line || universalResult?.compile?.error_line || diagnosis?.line}
            />
          </div>

          {/* Bottom Dock: Terminal & Problems */}
          <TerminalPanel
            filename={activeFile}
            execution={universalResult?.execution || null}
            compile={universalResult?.compile || null}
            diagnosis={diagnosis}
            stdin={stdin}
            onStdinChange={setStdin}
            onApplyFix={handleApplyFix}
            onExplainError={() => handleAskAI('explain')}
          />
        </div>

        {/* Right Side Dock: Compiler Inspector / Debugger / Analyzer / AI */}
        {activeSidebar === 'compiler' && (
          <CompilerPanel
            compileData={compileData}
            isLoading={isLoading}
            onRecompile={handleCompile}
          />
        )}

        {activeSidebar === 'debug' && (
          <DebuggerPanel
            isDebugging={isDebugging}
            debugState={debugState}
            breakpoints={breakpoints}
            onToggleBreakpoint={handleToggleBreakpoint}
            onStepOver={handleStepOver}
            onContinue={handleRun}
            onStop={() => setIsDebugging(false)}
            onRestart={handleDebug}
          />
        )}

        {activeSidebar === 'ast' && (
          <AnalyzerPanel
            ast={universalResult?.ast || null}
            complexity={universalResult?.complexity || null}
            security={universalResult?.security || null}
            quality={universalResult?.quality || null}
          />
        )}

        {activeSidebar === 'ai' && (
          <AIAssistantPanel
            onAskAI={handleAskAI}
            aiResponse={aiResponse}
            isLoading={aiLoading}
            onApplyCode={(newCode) => {
              handleCodeChange(newCode);
              handleRun();
            }}
          />
        )}
      </div>

      {/* Project Version History & Cloud Hub Modal */}
      <ProjectHistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        projectId={currentProjectId}
        projectTitle={projectTitle}
        onRestoreProject={handleRestoreProject}
        onLoadTemplate={handleLoadTemplate}
      />

      {/* Full Analysis Workspace Modal */}
      <AnalysisModal
        isOpen={isAnalysisOpen}
        onClose={() => setIsAnalysisOpen(false)}
        result={universalResult}
        code={currentCode}
        onAskAI={handleAskAI}
        onApplyFix={handleApplyFix}
      />

      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onFileUploaded={handleSingleFileUploaded}
        onProjectUploaded={handleProjectUploaded}
      />

      {/* Project Report Modal */}
      <ProjectReportModal
        report={projectReport}
        isOpen={isProjectReportOpen}
        onClose={() => setIsProjectReportOpen(false)}
        onOpenFileInEditor={handleOpenFileFromReport}
      />
    </div>
  );
};

export default App;
