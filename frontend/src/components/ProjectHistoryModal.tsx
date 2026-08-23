import React, { useState, useEffect } from 'react';
import { 
  History, 
  RotateCcw, 
  Camera, 
  Download, 
  Share2, 
  X, 
  Check, 
  Copy, 
  Clock, 
  Layers, 
  FileCode, 
  BookOpen, 
  Sparkles,
  ChevronRight,
  ShieldAlert,
  Loader2
} from 'lucide-react';
import { ProjectVersion, ProjectTemplate, ProjectDetails } from '../types';
import { apiService } from '../services/api';

interface ProjectHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  projectTitle: string;
  onRestoreProject: (project: ProjectDetails) => void;
  onLoadTemplate: (template: ProjectTemplate) => void;
}

export const ProjectHistoryModal: React.FC<ProjectHistoryModalProps> = ({
  isOpen,
  onClose,
  projectId,
  projectTitle,
  onRestoreProject,
  onLoadTemplate,
}) => {
  const [activeTab, setActiveTab] = useState<'history' | 'templates' | 'share'>('history');
  const [versions, setVersions] = useState<ProjectVersion[]>([]);
  const [templates, setTemplates] = useState<ProjectTemplate[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<ProjectVersion | null>(null);
  const [snapshotTag, setSnapshotTag] = useState('');
  const [snapshotSummary, setSnapshotSummary] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [shareUrl, setShareUrl] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen && projectId) {
      loadHistory();
      loadTemplates();
    }
  }, [isOpen, projectId]);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const vList = await apiService.getProjectVersions(projectId);
      setVersions(vList);
      if (vList.length > 0) {
        setSelectedVersion(vList[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const tList = await apiService.getProjectTemplates();
      setTemplates(tList);
    } catch (e) {
      console.error(e);
    }
  };

  if (!isOpen) return null;

  const handleCreateSnapshot = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!snapshotTag.trim()) return;
    setIsLoading(true);
    try {
      await apiService.createProjectSnapshot(projectId, snapshotTag, snapshotSummary);
      setSnapshotTag('');
      setSnapshotSummary('');
      await loadHistory();
    } catch (e: any) {
      alert('Failed to create snapshot: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestore = async (vId: string) => {
    if (!confirm('Restore project to this snapshot version? (A safety point of your current code will be saved automatically).')) return;
    setIsLoading(true);
    try {
      const restored = await apiService.restoreProjectVersion(projectId, vId);
      onRestoreProject(restored);
      onClose();
    } catch (e: any) {
      alert('Failed to restore: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateShare = async () => {
    setIsLoading(true);
    try {
      const res = await apiService.shareProject(projectId);
      const fullUrl = `${window.location.origin}${res.share_url}`;
      setShareUrl(fullUrl);
    } catch (e: any) {
      alert('Failed to generate share link: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyShare = () => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in select-none">
      <div className="w-full max-w-4xl bg-[#0E1424] border border-gray-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-6 py-4 bg-[#12182D] border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>{projectTitle}</span>
                <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-mono">
                  Cloud Hub
                </span>
              </h2>
              <p className="text-xs text-gray-400">Version History Snapshots • Export & Sharing • Starter Templates</p>
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
        <div className="px-6 border-b border-gray-800 bg-[#0A0F1D] flex items-center gap-2 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('history')}
            className={`py-3 px-3 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'history' ? 'border-blue-500 text-blue-400 font-bold' : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <History className="w-4 h-4" />
            <span>Version History ({versions.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`py-3 px-3 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'templates' ? 'border-purple-500 text-purple-400 font-bold' : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Starter Templates ({templates.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('share')}
            className={`py-3 px-3 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'share' ? 'border-emerald-500 text-emerald-400 font-bold' : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Share2 className="w-4 h-4" />
            <span>Export & Share</span>
          </button>
        </div>

        {/* Tab Body */}
        <div className="flex-1 overflow-y-auto p-6 font-sans text-xs select-text">
          {/* TAB 1: Version History */}
          {activeTab === 'history' && (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
              {/* Left Column: Create Snapshot + Versions List */}
              <div className="md:col-span-5 space-y-4">
                {/* Take Snapshot Form */}
                <form onSubmit={handleCreateSnapshot} className="p-3.5 bg-black/40 rounded-xl border border-gray-800 space-y-2.5">
                  <div className="flex items-center gap-1.5 font-bold text-gray-200 text-xs">
                    <Camera className="w-3.5 h-3.5 text-blue-400" />
                    <span>Create Named Snapshot</span>
                  </div>
                  <input
                    type="text"
                    placeholder="Tag name (e.g. v1.0 Milestone, Before Refactor)"
                    value={snapshotTag}
                    onChange={(e) => setSnapshotTag(e.target.value)}
                    required
                    className="w-full px-2.5 py-1.5 rounded-lg bg-gray-900 border border-gray-700 text-white font-sans text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    placeholder="Optional summary / changelog..."
                    value={snapshotSummary}
                    onChange={(e) => setSnapshotSummary(e.target.value)}
                    className="w-full px-2.5 py-1.5 rounded-lg bg-gray-900 border border-gray-700 text-gray-300 font-sans text-[11px] focus:outline-none"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !snapshotTag.trim()}
                    className="w-full py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
                  >
                    Save Snapshot Version
                  </button>
                </form>

                {/* Timeline List */}
                <div className="space-y-2 max-h-[340px] overflow-y-auto pr-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block">Revision Timeline</span>
                  {versions.length === 0 ? (
                    <div className="text-gray-500 italic p-4 text-center">No snapshots recorded yet.</div>
                  ) : (
                    versions.map((v) => (
                      <div
                        key={v.id}
                        onClick={() => setSelectedVersion(v)}
                        className={`p-3 rounded-xl border transition-all cursor-pointer space-y-1 ${
                          selectedVersion?.id === v.id
                            ? 'bg-blue-950/30 border-blue-500/50 shadow-md'
                            : 'bg-gray-900/50 border-gray-800 hover:bg-gray-900'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-white text-xs">{v.version_tag}</span>
                          <span className="text-[10px] text-gray-400 font-mono">
                            {new Date(v.created_at * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                          </span>
                        </div>
                        <p className="text-gray-400 text-[11px] line-clamp-1">{v.summary}</p>
                        <div className="flex items-center gap-3 text-[10px] text-gray-500 font-mono pt-0.5">
                          <span>{v.files_count} file(s)</span>
                          <span>•</span>
                          <span>{v.total_loc} LOC</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Right Column: Selected Version Preview & Restore */}
              <div className="md:col-span-7 flex flex-col min-h-0 bg-black/50 rounded-2xl border border-gray-800 p-4 space-y-3">
                {selectedVersion ? (
                  <>
                    <div className="flex items-center justify-between border-b border-gray-800 pb-2.5">
                      <div>
                        <h4 className="font-bold text-white text-sm">{selectedVersion.version_tag}</h4>
                        <span className="text-[11px] text-gray-400">
                          Captured {new Date(selectedVersion.created_at * 1000).toLocaleString()}
                        </span>
                      </div>
                      <button
                        onClick={() => handleRestore(selectedVersion.id)}
                        disabled={isLoading}
                        className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md transition-all active:scale-95 disabled:opacity-50"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span>Restore This Version</span>
                      </button>
                    </div>

                    <div className="flex-1 overflow-y-auto space-y-3 max-h-[300px]">
                      {selectedVersion.files.map((f, idx) => (
                        <div key={idx} className="rounded-xl bg-[#090D18] border border-gray-800 overflow-hidden">
                          <div className="px-3 py-1.5 bg-[#101526] border-b border-gray-800 flex items-center justify-between text-xs font-mono">
                            <span className="text-gray-300 font-bold">{f.name}</span>
                            <span className="text-blue-400 uppercase text-[10px]">{f.language}</span>
                          </div>
                          <pre className="p-3 text-[11px] font-mono text-gray-300 whitespace-pre-wrap overflow-x-auto max-h-40">
                            {f.content}
                          </pre>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-gray-500 italic">
                    Select a snapshot from the timeline to preview and restore.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: Starter Templates */}
          {activeTab === 'templates' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.map((tmpl) => (
                  <div
                    key={tmpl.id}
                    className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800 hover:border-purple-500/50 hover:bg-purple-950/10 transition-all space-y-3 flex flex-col justify-between"
                  >
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white text-sm">{tmpl.title}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-purple-500/20 text-purple-300 font-mono">
                          {tmpl.language}
                        </span>
                      </div>
                      <span className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider block">
                        {tmpl.category} • {tmpl.difficulty}
                      </span>
                      <p className="text-gray-300 text-xs leading-relaxed">{tmpl.description}</p>
                    </div>

                    <div className="pt-2 border-t border-gray-800 flex items-center justify-between">
                      <span className="text-[11px] text-gray-400 font-mono">{tmpl.files.length} file(s) included</span>
                      <button
                        onClick={() => {
                          onLoadTemplate(tmpl);
                          onClose();
                        }}
                        className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center gap-1 shadow transition-colors"
                      >
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Use Template</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Export & Sharing */}
          {activeTab === 'share' && (
            <div className="space-y-6 max-w-xl mx-auto">
              {/* ZIP Export Card */}
              <div className="p-4 rounded-2xl bg-blue-950/20 border border-blue-500/30 space-y-3">
                <div className="flex items-center gap-2 font-bold text-white text-sm">
                  <Download className="w-4 h-4 text-blue-400" />
                  <span>Export Project as ZIP Archive</span>
                </div>
                <p className="text-gray-300 text-xs">
                  Download all source files with complete project directory structure and CodePrism metadata.
                </p>
                <a
                  href={apiService.getExportZipUrl(projectId)}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download {projectTitle}.zip</span>
                </a>
              </div>

              {/* Shareable Link Card */}
              <div className="p-4 rounded-2xl bg-purple-950/20 border border-purple-500/30 space-y-3">
                <div className="flex items-center gap-2 font-bold text-white text-sm">
                  <Share2 className="w-4 h-4 text-purple-400" />
                  <span>Generate Public Portfolio Share Link</span>
                </div>
                <p className="text-gray-300 text-xs">
                  Anyone with this link can view, inspect Big-O analysis, and execute your code in their browser.
                </p>

                {shareUrl ? (
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      readOnly
                      value={shareUrl}
                      className="flex-1 px-3 py-2 rounded-xl bg-gray-900 border border-gray-700 text-emerald-300 font-mono text-xs focus:outline-none"
                    />
                    <button
                      onClick={handleCopyShare}
                      className="px-3.5 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white font-bold text-xs flex items-center gap-1.5 shadow transition-colors"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied!' : 'Copy'}</span>
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={handleGenerateShare}
                    disabled={isLoading}
                    className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow flex items-center gap-2 transition-colors disabled:opacity-50"
                  >
                    {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Share2 className="w-4 h-4" />}
                    <span>Generate Shareable Link</span>
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-[#0A0F1D] border-t border-gray-800 flex items-center justify-between">
          <span className="text-[11px] text-gray-500 font-mono">CodePrism Cloud Synchronization Engine</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-white font-bold text-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
