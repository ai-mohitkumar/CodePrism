import React, { useState, useRef } from 'react';
import { 
  Upload, 
  FileCode, 
  FolderArchive, 
  GitBranch, 
  X, 
  AlertCircle, 
  CheckCircle2, 
  Loader2, 
  Layers, 
  ArrowRight 
} from 'lucide-react';
import { apiService } from '../services/api';
import { FileUploadResponse, ProjectReportResponse } from '../types';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onFileUploaded: (res: FileUploadResponse) => void;
  onProjectUploaded: (res: ProjectReportResponse) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  onFileUploaded,
  onProjectUploaded,
}) => {
  const [activeTab, setActiveTab] = useState<'single' | 'project' | 'github'>('single');
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [githubUrl, setGithubUrl] = useState('');
  const [githubBranch, setGithubBranch] = useState('main');

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const zipInputRef = useRef<HTMLInputElement | null>(null);

  if (!isOpen) return null;

  const handleSingleFile = async (file: File) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await apiService.uploadFile(file);
      onFileUploaded(res);
      onClose();
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || err.message || 'File upload analysis failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleZipProject = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.zip')) {
      setErrorMessage('Project analysis requires a .zip archive.');
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await apiService.uploadProjectZip(file);
      onProjectUploaded(res);
      onClose();
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || err.message || 'Project ZIP analysis failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGitHubSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubUrl.startsWith('https://github.com/')) {
      setErrorMessage('Please enter a valid GitHub repository URL (e.g., https://github.com/user/repo).');
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await apiService.analyzeGitHubRepo(githubUrl, githubBranch);
      onProjectUploaded(res);
      onClose();
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || err.message || 'GitHub clone analysis failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.name.toLowerCase().endsWith('.zip')) {
        handleZipProject(file);
      } else {
        handleSingleFile(file);
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in select-none">
      <div className="w-full max-w-xl bg-[#0E1322] border border-gray-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-gray-800 bg-[#12182B] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/20">
              <Upload className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Upload & Analyze Code</h2>
              <p className="text-xs text-gray-400">Automatic Language Detection • Compilation • AST & Big-O Engine</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="px-6 border-b border-gray-800 bg-[#0A0E1A] flex items-center gap-2 text-xs font-semibold">
          <button
            onClick={() => { setActiveTab('single'); setErrorMessage(null); }}
            className={`py-3 px-3 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'single' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <FileCode className="w-4 h-4" />
            <span>Single File</span>
          </button>
          <button
            onClick={() => { setActiveTab('project'); setErrorMessage(null); }}
            className={`py-3 px-3 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'project' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <FolderArchive className="w-4 h-4" />
            <span>ZIP Project</span>
          </button>
          <button
            onClick={() => { setActiveTab('github'); setErrorMessage(null); }}
            className={`py-3 px-3 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'github' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <GitBranch className="w-4 h-4" />
            <span>GitHub Repo</span>
          </button>
        </div>

        {/* Modal Content Body */}
        <div className="p-6 space-y-4 font-sans text-xs">
          {errorMessage && (
            <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Single File Upload */}
          {activeTab === 'single' && (
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3 ${
                isDragging 
                  ? 'border-blue-500 bg-blue-500/10 scale-[0.99]' 
                  : 'border-gray-700/80 bg-gray-900/40 hover:border-gray-500 hover:bg-gray-900/60'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".py,.cpp,.c,.java,.js,.jsx,.ts,.tsx,.cs,.rs,.go,.kt,.swift,.php,.rb,.dart,.r,.sql,.sh"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleSingleFile(e.target.files[0]);
                  }
                }}
              />
              <div className="w-12 h-12 rounded-2xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                {isLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Upload className="w-6 h-6" />}
              </div>
              <div className="space-y-1">
                <span className="font-bold text-sm text-gray-200 block">
                  {isLoading ? 'Compiling & Analyzing Source...' : 'Click to Browse or Drag & Drop'}
                </span>
                <span className="text-gray-400 text-xs block">
                  Supported: .py, .cpp, .c, .java, .js, .ts, .cs, .rs, .go, .kt, .swift, .php, .rb, .dart, .r, .sql, .sh
                </span>
              </div>
              <button className="mt-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md transition-colors">
                Browse Files
              </button>
            </div>
          )}

          {/* Project ZIP Upload */}
          {activeTab === 'project' && (
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => zipInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3 ${
                isDragging 
                  ? 'border-indigo-500 bg-indigo-500/10 scale-[0.99]' 
                  : 'border-gray-700/80 bg-gray-900/40 hover:border-gray-500 hover:bg-gray-900/60'
              }`}
            >
              <input
                ref={zipInputRef}
                type="file"
                className="hidden"
                accept=".zip"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleZipProject(e.target.files[0]);
                  }
                }}
              />
              <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                {isLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <FolderArchive className="w-6 h-6" />}
              </div>
              <div className="space-y-1">
                <span className="font-bold text-sm text-gray-200 block">
                  {isLoading ? 'Scanning ZIP Tree & Dependencies...' : 'Select ZIP Project Archive'}
                </span>
                <span className="text-gray-400 text-xs block">
                  Extracts full repo structure, language distributions, and cross-file Big-O complexity
                </span>
              </div>
              <button className="mt-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition-colors">
                Browse ZIP Archive
              </button>
            </div>
          )}

          {/* GitHub Repo Analyzer */}
          {activeTab === 'github' && (
            <form onSubmit={handleGitHubSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-gray-300 font-semibold block">GitHub Repository URL</label>
                <input
                  type="url"
                  placeholder="https://github.com/username/repository"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  required
                  className="w-full px-3 py-2 rounded-xl bg-gray-900 border border-gray-700 text-white font-mono text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-gray-300 font-semibold block">Branch</label>
                <input
                  type="text"
                  placeholder="main"
                  value={githubBranch}
                  onChange={(e) => setGithubBranch(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-gray-900 border border-gray-700 text-white font-mono text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <GitBranch className="w-4 h-4" />}
                <span>{isLoading ? 'Cloning & Analyzing Repository...' : 'Clone & Analyze Repository'}</span>
              </button>
            </form>
          )}

          {/* Feature Badges Footer */}
          <div className="pt-2 border-t border-gray-800 grid grid-cols-3 gap-2 text-center text-[11px] text-gray-400">
            <div className="flex items-center justify-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Auto-Detect Lang</span>
            </div>
            <div className="flex items-center justify-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
              <span>Exact Error Pointers</span>
            </div>
            <div className="flex items-center justify-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-purple-400" />
              <span>Big-O & Security</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
